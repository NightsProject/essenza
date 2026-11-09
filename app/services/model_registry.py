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
        model_id: Literal["baseline", "finetuned"],
        label: str,
        path: Path,
        tokenizer=None,
        model=None,
        device: str = "unknown",
        error: str | None = None,
    ):
        self.model_id = model_id
        self.label = label
        self.path = path
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
    - "both": Load both models at startup (default)
    - "serialized": Load models on first use (for memory-constrained environments)
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.device = self._resolve_device(settings.device)
        self.models: dict[str, ModelInfo] = {}
        self._initialized = False

        # Register known models
        self.models["baseline"] = ModelInfo(
            model_id="baseline",
            label="Baseline FLAN-T5-small",
            path=settings.baseline_model_path,
        )
        self.models["finetuned"] = ModelInfo(
            model_id="finetuned",
            label="Fine-tuned FLAN-T5-small",
            path=settings.finetuned_model_path,
        )

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
            await self._load_model("baseline")
            await self._load_model("finetuned")
        elif strategy == "serialized":
            # Models loaded on demand in get_model()
            pass
        else:
            logger.warning("Unknown model_load_strategy: %s, defaulting to 'both'", strategy)
            await self._load_model("baseline")
            await self._load_model("finetuned")

        self._initialized = True
        logger.info("Model registry initialized (device=%s, strategy=%s)", self.device, strategy)

    async def _load_model(self, model_id: Literal["baseline", "finetuned"]):
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

    def get_model(self, model_id: Literal["baseline", "finetuned"]) -> ModelInfo:
        """Get model info, loading on demand if strategy is serialized."""
        info = self.models[model_id]

        if not info.loaded and self.settings.model_load_strategy == "serialized":
            import asyncio
            asyncio.create_task(self._load_model(model_id))

        return info

    def is_ready(self, model_id: Literal["baseline", "finetuned"]) -> bool:
        """Check if model is loaded and ready."""
        return self.models[model_id].loaded

    def get_model_info(self, model_id: Literal["baseline", "finetuned"]) -> dict:
        """Get model metadata for health endpoint."""
        info = self.models[model_id]
        return {
            "label": info.label,
            "loaded": info.loaded,
            "device": info.device,
            "error": info.error,
            "path": str(info.path),
        }

    async def shutdown(self):
        """Clean up model references."""
        for info in self.models.values():
            info.model = None
            info.tokenizer = None
            info._loaded = False

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info("Model registry shut down")