# app/config.py — Environment-based configuration via Pydantic Settings

from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "essenza"
    version: str = "0.1.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # Model paths (directories containing config.json, pytorch_model.bin, tokenizer files)
    baseline_model_path: Path = Field(
        default=Path("./app/models/baseline"),
        description="Directory with baseline FLAN-T5-small checkpoint",
    )
    finetuned_model_path: Path = Field(
        default=Path("./app/models/finetuned"),
        description="Directory with fine-tuned FLAN-T5-small checkpoint",
    )

    # Model loading strategy: "both" (load both at startup) | "serialized" (load on demand)
    model_load_strategy: str = Field(
        default="both",
        description="Model loading strategy: 'both' or 'serialized'",
    )

    # Inference settings
    max_input_tokens: int = Field(default=512, description="Maximum input tokens (matches notebook)")
    max_output_tokens: int = Field(default=128, description="Maximum generated tokens (matches notebook)")
    num_beams: int = Field(default=4, description="Beam search width for deterministic generation")
    do_sample: bool = Field(default=False, description="Use sampling vs deterministic beam search")
    temperature: float = Field(default=1.0, description="Sampling temperature (ignored if do_sample=False)")

    # Device: "auto" | "cuda" | "cpu" | "mps"
    device: str = Field(default="auto", description="Inference device")

    # Request limits
    max_request_size_mb: int = Field(default=1, description="Max request body size in MB")

    # Paths
    templates_dir: Path = Field(default=Path("./app/templates"))
    static_dir: Path = Field(default=Path("./app/static"))

    # Compression thresholds (validated in schemas)
    allowed_thresholds: tuple[int, ...] = (10, 20, 30)

    # Prompt template (must match notebook)
    prompt_template: str = Field(
        default="summarize to at most {percent}%: {text}",
        description="Prompt template; {percent} and {text} are placeholders",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()