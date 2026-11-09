# Decision: API Contracts — Request/Response Schemas & Health Endpoint

## Context
The design document (section 8.3, 8.4) defines API routes and request/response contracts. This decision formalizes the Pydantic schemas, validation rules, error format, and health endpoint structure.

## Decision
Define all API contracts in `app/schemas/summarization.py` using Pydantic v2. Use strict validation, explicit error messages, and consistent response envelopes.

## Request Schemas

### Single-Model Summarization Request
```python
class SummarizeRequest(BaseModel):
    source_text: str = Field(..., min_length=1, description="Text to summarize")
    max_compression_percent: Literal[10, 20, 30] = Field(..., description="Maximum summary length as percentage of source")
    model_id: Literal["finetuned"] = Field(default="finetuned", description="Model to use (single-model mode only)")
```

### Comparison Request
```python
class CompareRequest(BaseModel):
    source_text: str = Field(..., min_length=1)
    max_compression_percent: Literal[10, 20, 30]
```

## Response Schemas

### Single Model Result
```python
class SummarizeResult(BaseModel):
    model_id: Literal["finetuned"]
    model_label: str = "Fine-tuned FLAN-T5-small"
    summary: str
    summary_word_count: int
    actual_compression_percent: float
    within_limit: bool
    generation_time_ms: int
    request_id: str
```

### Comparison Result
```python
class CompareResult(BaseModel):
    model_id: Literal["baseline", "finetuned"]
    model_label: str  # "Baseline FLAN-T5-small" | "Fine-tuned FLAN-T5-small"
    summary: str
    summary_word_count: int
    actual_compression_percent: float
    within_limit: bool
    generation_time_ms: int
    error: str | None = None  # Populated only if this model failed
```

### Comparison Response
```python
class CompareResponse(BaseModel):
    max_compression_percent: int
    source_word_count: int
    results: list[CompareResult]  # Always 2 items (baseline, finetuned)
    request_id: str
```

### Error Response
```python
class ErrorDetail(BaseModel):
    code: str  # e.g., "VALIDATION_ERROR", "MODEL_UNAVAILABLE", "TOKEN_LIMIT_EXCEEDED", "GENERATION_TIMEOUT"
    message: str
    field: str | None = None
    details: dict | None = None

class ErrorResponse(BaseModel):
    error: ErrorDetail
    request_id: str
```

### Health Response
```python
class ModelStatus(BaseModel):
    model_id: Literal["baseline", "finetuned"]
    model_label: str
    loaded: bool
    device: str  # "cuda" | "cpu"
    error: str | None = None

class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    models: list[ModelStatus]
    device: str  # Primary device for inference
    uptime_seconds: float
```

## Validation Rules

| Field | Rule | Error Code |
|-------|------|------------|
| `source_text` | Non-empty after strip | `VALIDATION_ERROR` |
| `source_text` | ≤ 512 tokens (validated server-side) | `TOKEN_LIMIT_EXCEEDED` |
| `max_compression_percent` | Must be 10, 20, or 30 | `VALIDATION_ERROR` |
| Request body | Valid JSON, required fields present | `VALIDATION_ERROR` |

## Error Handling

- **422 Unprocessable Entity**: Validation errors (field-level details in `ErrorDetail`)
- **503 Service Unavailable**: Model not loaded (`MODEL_UNAVAILABLE`)
- **504 Gateway Timeout**: Generation timeout (`GENERATION_TIMEOUT`)
- **500 Internal Server Error**: Unexpected errors (logged, generic message returned)

## Health Endpoint Contract

`GET /health` returns `HealthResponse`:
- `status`: "healthy" (both models loaded), "degraded" (one model loaded), "unhealthy" (neither loaded)
- Never exposes filesystem paths, secrets, or environment variables
- Includes uptime for monitoring

## Consequences
- Strict validation prevents invalid requests from reaching model runtime
- Request IDs enable log correlation across services
- Error codes allow client-side handling without parsing messages
- Health endpoint supports load balancer readiness probes

## Alternatives Considered
- **OpenAPI-only contracts**: Rejected — Pydantic provides runtime validation + type safety
- **Union types for model_id**: Rejected — Literal provides better validation + OpenAPI enum
- **Separate error schema per endpoint**: Rejected — consistent envelope simplifies clients

## Status
**Accepted** — Implement in `app/schemas/summarization.py`.

## Implementation Notes
- Use `pydantic.Field` with `description` for OpenAPI documentation
- Add `model_config = ConfigDict(extra="forbid")` to all request models
- `request_id`: generate ULID at route entry, pass through services
- Token validation: use tokenizer to count tokens, not character length