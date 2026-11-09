# app/services/model_registry.py — Load and manage model instances

import logging
import torch
from pathlib import Path
from typing import Literal

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from app.config import Settings

logger = logging.getLogger("essenza.model_registry")


class ModelInfo:
    def __init__(
        self,
        model_id: str,
        label: str,
        path: Path,
        model_type: Literal["baseline", "finetuned"],
        tokenizer=None,
        model=None,
        device: str = "unknown",
        error: str | None = None,
    ):
        self.model_id = model_id
        self.label = label
        self.path = path
        self.model_type = model_type
        self.tokenizer = tokenizer
        self.model = model
        self.device = device
        self.error = error
        self._loaded = False

    @property
    def loaded(self) -> bool:
        return self._loaded and self.model is not None and self.tokenizer is not None

    def mark_loaded(self, device: str):
        self._loaded = True
        self.device = device
        self.error = None

    def mark_error(self, error: str):
        self._loaded = False
        self.error = error
        self.model = None
        self.tokenizer = None


class ModelRegistry:
    """
    Loads and manages model checkpoints at startup.

    Supports two strategies:
    - "both": Load all models at startup (default)
    - "serialized": Load models on first use (for memory-constrained environments)

    Finetuned models are auto-discovered from subdirectories under the finetuned model path.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.device = self._resolve_device(settings.device)
        self.models: dict[str, ModelInfo] = {}
        self._initialized = False

        # Register baseline model (single)
        self.models["baseline"] = ModelInfo(
            model_id="baseline",
            label="Baseline FLAN-T5-small",
            path=settings.baseline_model_path,
            model_type="baseline",
        )

        # Discover and register finetuned models from subdirectories
        self._discover_finetuned_models()

    def _discover_finetuned_models(self):
        """Scan finetuned_model_path for subdirectories containing model checkpoints."""
        finetuned_root = self.settings.finetuned_model_path

        if not finetuned_root.exists():
            logger.warning("Finetuned model root does not exist: %s", finetuned_root)
            return

        # Look for subdirectories that contain a config.json (indicating a model checkpoint)
        for subdir in sorted(finetuned_root.iterdir()):
            if subdir.is_dir() and (subdir / "config.json").exists():
                model_id = f"finetuned:{subdir.name}"
                label = f"Fine-tuned: {subdir.name}"
                self.models[model_id] = ModelInfo(
                    model_id=model_id,
                    label=label,
                    path=subdir,
                    model_type="finetuned",
                )
                logger.info("Discovered finetuned model: %s at %s", model_id, subdir)

        # Fallback: if no subdirectories found but root has config.json, register root as single finetuned
        if not any(m.model_type == "finetuned" for m in self.models.values()):
            if (finetuned_root / "config.json").exists():
                self.models["finetuned"] = ModelInfo(
                    model_id="finetuned",
                    label="Fine-tuned FLAN-T5-small",
                    path=finetuned_root,
                    model_type="finetuned",
                )
                logger.info("Registered single finetuned model at root: %s", finetuned_root)
            else:
                logger.warning("No finetuned models found at %s", finetuned_root)

    def _resolve_device(self, device_setting: str) -> str:
        if device_setting == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
            return "cpu"
        return device_setting

    async def initialize(self):
        """Load models based on strategy."""
        if self._initialized:
            return

        strategy = self.settings.model_load_strategy

        if strategy == "both":
            for model_id in self.models:
                await self._load_model(model_id)
        elif strategy == "serialized":
            # Models loaded on demand in get_model()
            pass
        else:
            logger.warning("Unknown model_load_strategy: %s, defaulting to 'both'", strategy)
            for model_id in self.models:
                await self._load_model(model_id)

        self._initialized = True
        loaded_count = sum(1 for m in self.models.values() if m.loaded)
        logger.info("Model registry initialized (device=%s, strategy=%s, models=%d, loaded=%d)",
                    self.device, strategy, len(self.models), loaded_count)

    async def _load_model(self, model_id: str):
        """Load a single model and tokenizer."""
        info = self.models[model_id]

        if info.loaded:
            return

        if not info.path.exists():
            error = f"Model path does not exist: {info.path}"
            logger.error(error)
            info.mark_error(error)
            return

        try:
            logger.info("Loading %s from %s...", model_id, info.path)

            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(str(info.path), local_files_only=True)

            # Load model
            model = AutoModelForSeq2SeqLM.from_pretrained(
                str(info.path),
                local_files_only=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True,
            )

            # Move to device
            model = model.to(self.device)
            model.eval()

            # Disable gradients for inference
            for param in model.parameters():
                param.requires_grad = False

            info.tokenizer = tokenizer
            info.model = model
            info.mark_loaded(self.device)

            logger.info("Loaded %s on %s", model_id, self.device)

        except Exception as e:
            error = f"Failed to load {model_id}: {e}"
            logger.exception(error)
            info.mark_error(error)

    def get_model(self, model_id: str) -> ModelInfo:
        """Get model info, loading on demand if strategy is serialized."""
        if model_id not in self.models:
            raise KeyError(f"Unknown model_id: {model_id}. Available: {list(self.models.keys())}")

        info = self.models[model_id]

        if not info.loaded and self.settings.model_load_strategy == "serialized":
            import asyncio
            asyncio.create_task(self._load_model(model_id))

        return info

    def is_ready(self, model_id: str) -> bool:
        """Check if model is loaded and ready."""
        if model_id not in self.models:
            return False
        return self.models[model_id].loaded

    def get_model_info(self, model_id: str) -> dict:
        """Get model metadata for health endpoint."""
        if model_id not in self.models:
            return {"label": model_id, "loaded": False, "device": "unknown", "error": "Unknown model", "path": ""}

        info = self.models[model_id]
        return {
            "model_id": info.model_id,
            "label": info.label,
            "model_type": info.model_type,
            "loaded": info.loaded,
            "device": info.device,
            "error": info.error,
            "path": str(info.path),
        }

    def get_all_models(self) -> list[dict]:
        """Get info for all registered models."""
        return [self.get_model_info(mid) for mid in self.models]

    def get_finetuned_models(self) -> list[dict]:
        """Get info for all finetuned models only."""
        return [self.get_model_info(mid) for mid, info in self.models.items() if info.model_type == "finetuned"]

    def get_baseline_model(self) -> dict:
        """Get info for baseline model."""
        return self.get_model_info("baseline")

    async def shutdown(self):
        """Clean up model references."""
        for info in self.models.values():
            info.model = None
            info.tokenizer = None
            info._loaded = False

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info("Model registry shut down")