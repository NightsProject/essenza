# Decision: Testing Strategy — Layers, Fixtures, Research Consistency

## Context
The design document (section 12) defines a testing strategy across unit, service, API, UI, research consistency, and performance levels. This decision formalizes the test structure, tools, and acceptance criteria.

## Decision
Use pytest with asyncio for all test layers. Organize tests in `app/tests/` mirroring source structure. Define fixtures for model registry, tokenizer, and test client.

## Test Layers

### 1. Unit Tests (`app/tests/test_metrics.py`, `test_validation.py`)
- **Scope**: Pure functions, no external dependencies
- **Coverage**:
  - Word counting (match notebook convention)
  - Compression ratio calculation
  - Cap compliance evaluation
  - Prompt construction
  - Threshold validation (10/20/30 only)
  - Token limit validation (512 tokens)
- **Tools**: pytest, no mocks needed
- **Speed**: < 1s total

### 2. Service Tests (`app/tests/test_services.py`)
- **Scope**: Services with mocked model runtime
- **Coverage**:
  - ModelRegistry loading (mock transformers)
  - Summarizer prompt building, tokenization
  - Deterministic generation config
  - Device selection logic
  - MetricsService integration
- **Tools**: pytest, unittest.mock, transformers testing utilities
- **Speed**: < 5s total

### 3. API Tests (`app/tests/test_routes.py`)
- **Scope**: Full FastAPI app via httpx.AsyncClient
- **Coverage**:
  - Valid request → 200 + correct response shape
  - Empty source_text → 422
  - Invalid threshold (5, 50, "high") → 422
  - Over-limit input (>512 tokens) → 422
  - Model unavailable → 503
  - Compare endpoint returns both models
  - Compare partial failure → one result + error
  - Health endpoint structure
- **Tools**: pytest, httpx, pytest-asyncio
- **Speed**: < 10s total

### 4. UI Tests (Manual + Playwright if needed)
- **Scope**: Browser rendering, interactions
- **Coverage**:
  - Responsive layout (mobile/desktop)
  - Selector behavior (threshold, model mode)
  - Loading state during generation
  - Error state display
  - Copy button functionality
  - Keyboard navigation
  - Screen-reader announcements
- **Tools**: Playwright (optional), manual verification
- **Speed**: Manual

### 5. Research Consistency Tests
- **Scope**: Ensure web app matches Colab notebook
- **Coverage**:
  - Prompt format: `summarize to at most {N}%: {text}`
  - Threshold semantics: 10/20/30 as maximums
  - Token limits: 512 input, 128 output
  - Word count convention matches notebook
  - Decoding: num_beams=4, do_sample=False
- **Tools**: pytest with notebook reference values
- **Speed**: < 5s

### 6. Performance Tests (Phase 6)
- **Scope**: Latency, memory, concurrency on target hardware
- **Coverage**:
  - Cold-start model load time
  - Warm inference latency (p50, p95, p99)
  - Memory usage (VRAM/RAM)
  - Concurrent request behavior (serialized)
- **Tools**: Custom script, not in CI
- **Speed**: Minutes

## Fixtures

```python
# conftest.py
@pytest.fixture(scope="session")
def test_tokenizer():
    return AutoTokenizer.from_pretrained("google/flan-t5-small")

@pytest.fixture(scope="session")
def mock_model_registry():
    # Returns ModelRegistry with mocked models
    pass

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

## Test Commands

```bash
# All tests
uv run pytest app/tests -v

# Unit only
uv run pytest app/tests/test_metrics.py app/tests/test_validation.py -v

# Service only
uv run pytest app/tests/test_services.py -v

# API only
uv run pytest app/tests/test_routes.py -v

# With coverage
uv run pytest app/tests --cov=app --cov-report=term-missing
```

## CI Integration (Future)
- Run unit + service + API on every push
- Research consistency on PR to main
- Performance manually in Phase 6

## Consequences
- Clear separation: unit (fast, no deps) vs service (mocked) vs API (integrated)
- Fixtures enable reusable test setup
- Research consistency prevents drift from notebook
- Performance tests separate from functional CI

## Alternatives Considered
- **Unittest**: Rejected — pytest fixtures + asyncio superior
- **Integration tests with real models**: Rejected — slow, flaky, needs GPU in CI
- **No research consistency tests**: Rejected — drift risk is high

## Status
**Accepted** — Implement fixtures and test files in Phase 1.

## Implementation Notes
- Create `app/tests/conftest.py` with shared fixtures
- Use `pytest-asyncio` for async route tests
- Mock `transformers.AutoModelForSeq2SeqLM.from_pretrained` in service tests
- Token validation tests use real tokenizer (fast, no model weights)