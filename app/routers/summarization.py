# app/routers/summarization.py — POST /api/summarize, /api/compare, GET /health

import uuid
import time
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.schemas.summarization import (
    SummarizeRequest,
    CompareRequest,
    SummarizeResult,
    CompareResponse,
    HealthResponse,
    ModelStatus,
    ErrorResponse,
    ErrorDetail,
    CompareResult,
)
from app.services.model_registry import ModelRegistry
from app.services.summarizer import Summarizer
from app.services.metrics import MetricsService


router = APIRouter()


def get_model_registry(request: Request) -> ModelRegistry:
    return request.app.state.model_registry


def get_settings(request: Request):
    return request.app.state.settings


@router.post(
    "/api/summarize",
    response_model=SummarizeResult,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        503: {"model": ErrorResponse, "description": "Model unavailable"},
        504: {"model": ErrorResponse, "description": "Generation timeout"},
    },
    name="summarize",
)
async def summarize(request: Request, payload: SummarizeRequest):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id

    settings = get_settings(request)
    model_registry = get_model_registry(request)

    # Validate model availability
    if not model_registry.is_ready("finetuned"):
        model_info = model_registry.get_model_info("finetuned")
        error_detail = model_info.get("error", "Fine-tuned model is not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="MODEL_UNAVAILABLE",
                    message="Fine-tuned model is not loaded",
                    details={"model_id": "finetuned", "error": error_detail, "path": str(settings.finetuned_model_path)},
                ),
                request_id=request_id,
            ).model_dump(),
        )

    # Token limit validation (approximate via word count * 1.3)
    # Actual token validation happens in Summarizer with real tokenizer
    summarizer = Summarizer(model_registry, settings)
    metrics = MetricsService()

    try:
        start_time = time.perf_counter()
        result = await summarizer.summarize(
            source_text=payload.source_text,
            max_compression_percent=payload.max_compression_percent,
            model_id="finetuned",
        )
        generation_time_ms = int((time.perf_counter() - start_time) * 1000)

        source_word_count = metrics.count_words(payload.source_text)
        summary_word_count = metrics.count_words(result.summary)
        actual_compression = metrics.compression_ratio(source_word_count, summary_word_count)
        within_limit = metrics.within_cap(actual_compression, payload.max_compression_percent)

        return SummarizeResult(
            summary=result.summary,
            summary_word_count=summary_word_count,
            actual_compression_percent=actual_compression,
            within_limit=within_limit,
            generation_time_ms=generation_time_ms,
            request_id=request_id,
        )

    except ValueError as e:
        # Token limit exceeded
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="TOKEN_LIMIT_EXCEEDED",
                    message=str(e),
                ),
                request_id=request_id,
            ).model_dump(),
        )
    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="GENERATION_TIMEOUT",
                    message="Generation timed out",
                ),
                request_id=request_id,
            ).model_dump(),
        )
    except Exception as e:
        # Logged by global handler
        raise


@router.post(
    "/api/compare",
    response_model=CompareResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        503: {"model": ErrorResponse, "description": "One or both models unavailable"},
        504: {"model": ErrorResponse, "description": "Generation timeout"},
    },
    name="compare",
)
async def compare(request: Request, payload: CompareRequest):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id

    settings = get_settings(request)
    model_registry = get_model_registry(request)

    # Check model availability
    baseline_ready = model_registry.is_ready("baseline")
    finetuned_ready = model_registry.is_ready("finetuned")

    if not baseline_ready and not finetuned_ready:
        baseline_info = model_registry.get_model_info("baseline")
        finetuned_info = model_registry.get_model_info("finetuned")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="MODEL_UNAVAILABLE",
                    message="Neither model is loaded",
                    details={
                        "baseline": {"error": baseline_info.get("error", "Not loaded"), "path": str(settings.baseline_model_path)},
                        "finetuned": {"error": finetuned_info.get("error", "Not loaded"), "path": str(settings.finetuned_model_path)},
                    },
                ),
                request_id=request_id,
            ).model_dump(),
        )

    summarizer = Summarizer(model_registry, settings)
    metrics = MetricsService()

    source_word_count = metrics.count_words(payload.source_text)
    results = []

    for model_id in ("baseline", "finetuned"):
        model_label = "Baseline FLAN-T5-small" if model_id == "baseline" else "Fine-tuned FLAN-T5-small"
        model_ready = baseline_ready if model_id == "baseline" else finetuned_ready

        if not model_ready:
            model_info = model_registry.get_model_info(model_id)
            error_detail = model_info.get("error", "Model not available")
            results.append(
                CompareResult(
                    model_id=model_id,
                    model_label=model_label,
                    summary="",
                    summary_word_count=0,
                    actual_compression_percent=0.0,
                    within_limit=False,
                    generation_time_ms=0,
                    error=f"{error_detail} (path: {model_info['path']})",
                )
            )
            continue

        try:
            start_time = time.perf_counter()
            result = await summarizer.summarize(
                source_text=payload.source_text,
                max_compression_percent=payload.max_compression_percent,
                model_id=model_id,
            )
            generation_time_ms = int((time.perf_counter() - start_time) * 1000)

            summary_word_count = metrics.count_words(result.summary)
            actual_compression = metrics.compression_ratio(source_word_count, summary_word_count)
            within_limit = metrics.within_cap(actual_compression, payload.max_compression_percent)

            results.append(
                CompareResult(
                    model_id=model_id,
                    model_label=model_label,
                    summary=result.summary,
                    summary_word_count=summary_word_count,
                    actual_compression_percent=actual_compression,
                    within_limit=within_limit,
                    generation_time_ms=generation_time_ms,
                    error=None,
                )
            )

        except ValueError as e:
            results.append(
                CompareResult(
                    model_id=model_id,
                    model_label=model_label,
                    summary="",
                    summary_word_count=0,
                    actual_compression_percent=0.0,
                    within_limit=False,
                    generation_time_ms=0,
                    error=str(e),
                )
            )
        except TimeoutError:
            results.append(
                CompareResult(
                    model_id=model_id,
                    model_label=model_label,
                    summary="",
                    summary_word_count=0,
                    actual_compression_percent=0.0,
                    within_limit=False,
                    generation_time_ms=0,
                    error="Generation timed out",
                )
            )
        except Exception as e:
            results.append(
                CompareResult(
                    model_id=model_id,
                    model_label=model_label,
                    summary="",
                    summary_word_count=0,
                    actual_compression_percent=0.0,
                    within_limit=False,
                    generation_time_ms=0,
                    error=f"Unexpected error: {e}",
                )
            )

    return CompareResponse(
        max_compression_percent=payload.max_compression_percent,
        source_word_count=source_word_count,
        results=results,
        request_id=request_id,
    )


@router.get("/health", response_model=HealthResponse, name="health")
async def health(request: Request):
    settings = get_settings(request)
    model_registry = get_model_registry(request)

    models_status = []
    loaded_count = 0

    for model_id in ("baseline", "finetuned"):
        ready = model_registry.is_ready(model_id)
        if ready:
            loaded_count += 1
        model_info = model_registry.get_model_info(model_id)
        models_status.append(
            ModelStatus(
                model_id=model_id,
                model_label=model_info["label"],
                loaded=ready,
                device=model_info.get("device", "unknown"),
                error=model_info.get("error"),
            )
        )

    if loaded_count == 2:
        status = "healthy"
    elif loaded_count == 1:
        status = "degraded"
    else:
        status = "unhealthy"

    uptime = time.time() - getattr(request.app.state, "start_time", time.time())

    return HealthResponse(
        status=status,
        version=settings.version,
        models=models_status,
        device=model_registry.device,
        uptime_seconds=uptime,
    )