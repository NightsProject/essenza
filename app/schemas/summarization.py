# app/schemas/summarization.py — Pydantic request/response models

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# Request Models
# =============================================================================

class SummarizeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_text: str = Field(
        ...,
        min_length=1,
        description="Text to summarize",
        examples=["Long article text to summarize..."],
    )
    max_compression_percent: Literal[10, 20, 30] = Field(
        ...,
        description="Maximum summary length as percentage of source word count",
        examples=[20],
    )
    model_id: str = Field(
        default="finetuned",
        description="Model to use (single-model mode only)",
    )


class CompareRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_text: str = Field(
        ...,
        min_length=1,
        description="Text to summarize",
        examples=["Long article text to summarize..."],
    )
    max_compression_percent: Literal[10, 20, 30] = Field(
        ...,
        description="Maximum summary length as percentage of source word count",
        examples=[20],
    )
    model_ids: list[str] | None = Field(
        default=None,
        description="Specific models to compare (default: all loaded models)",
    )


# =============================================================================
# Response Models
# =============================================================================

class BaseResult(BaseModel):
    model_id: str
    model_label: str
    summary: str
    summary_word_count: int
    actual_compression_percent: float
    within_limit: bool
    generation_time_ms: int
    error: str | None = None


class SummarizeResult(BaseModel):
    model_id: str
    model_label: str
    summary: str
    summary_word_count: int
    actual_compression_percent: float
    within_limit: bool
    generation_time_ms: int
    request_id: str


class CompareResult(BaseResult):
    pass


class CompareResponse(BaseModel):
    max_compression_percent: int
    source_word_count: int
    results: list[CompareResult] = Field(..., min_length=1)
    request_id: str


class ModelStatus(BaseModel):
    model_id: str
    model_label: str
    model_type: str
    loaded: bool
    device: str
    error: str | None = None


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    models: list[ModelStatus]
    device: str
    uptime_seconds: float


# =============================================================================
# Error Models
# =============================================================================

class ErrorDetail(BaseModel):
    code: str = Field(..., examples=["VALIDATION_ERROR", "MODEL_UNAVAILABLE", "TOKEN_LIMIT_EXCEEDED", "GENERATION_TIMEOUT"])
    message: str
    field: str | None = None
    details: dict | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
    request_id: str