# Essenza — Extreme Text Summarization Web Application

A browser-based interface for evaluating information-preserving extreme text summarization using FLAN-T5-small. Compare baseline and fine-tuned model outputs under maximum compression thresholds of 10%, 20%, and 30%.

## Research Question

> Does additional fine-tuning improve a pretrained Transformer's ability to preserve important facts when summarizing text under maximum length limits of 10%, 20%, and 30% of the source?

## Features

- **Two inference modes**: Single fine-tuned model or side-by-side baseline vs. fine-tuned comparison
- **Configurable compression**: Maximum summary length at 10%, 20%, or 30% of source word count
- **Real-time metrics**: Source/summary word counts, actual compression ratio, cap compliance status
- **Deterministic generation**: Beam search (num_beams=4, do_sample=False) for reproducible results
- **Responsive UI**: Works on desktop and mobile; comparison cards stack vertically on narrow screens
- **Accessible**: Semantic HTML, keyboard navigation, screen-reader announcements, focus management

## Quick Start

### Prerequisites

- Python 3.10+
- CUDA-enabled GPU (recommended) or CPU
- Model checkpoints exported from the Colab training notebook

### Installation

```bash
# Clone and enter project
git clone https://github.com/<your-username>/essenza.git
cd essenza

# Install dependencies (uses uv)
uv sync --dev

# Place model checkpoints in the expected locations:
# app/models/baseline/     # Original google/flan-t5-small
# app/models/finetuned/    # Fine-tuned checkpoint from Colab
```

### Running Locally

```bash
# Development server with auto-reload
uv run uvicorn app.main:app --reload --port 8000

# Production-style (single worker for model memory)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

Open <http://localhost:8000> in your browser.

### Health Check

```bash
curl http://localhost:8000/health
```

Returns model readiness status:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "models": [
    {"model_id": "baseline", "model_label": "Baseline FLAN-T5-small", "loaded": true, "device": "cuda"},
    {"model_id": "finetuned", "model_label": "Fine-tuned FLAN-T5-small", "loaded": true, "device": "cuda"}
  ],
  "device": "cuda",
  "uptime_seconds": 42.3
}
```

## Project Structure

```
essenza/
├── app/                          # FastAPI application
│   ├── main.py                   # Application entrypoint + lifespan
│   ├── config.py                 # Pydantic Settings (env vars)
│   ├── routers/
│   │   ├── pages.py              # GET /, /methodology, /about
│   │   └── summarization.py      # POST /api/summarize, /api/compare, GET /health
│   ├── schemas/
│   │   └── summarization.py      # Pydantic request/response models
│   ├── services/
│   │   ├── model_registry.py     # Load/manage model checkpoints
│   │   ├── summarizer.py         # Prompt, tokenize, generate, decode
│   │   └── metrics.py            # Word count, compression, cap compliance
│   ├── templates/                # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── methodology.html
│   │   └── about.html
│   ├── static/
│   │   ├── css/styles.css        # Design system
│   │   └── js/app.js             # Frontend interactions
│   └── models/
│       ├── baseline/             # Baseline model artifacts
│       └── finetuned/            # Fine-tuned model artifacts
├── docs/design/                  # Decision records
│   ├── decision-roadmap.md
│   ├── decision-api-contracts.md
│   ├── decision-deployment.md
│   └── decision-testing.md
├── plans/                        # Phase plans
│   └── phase-1-project-setup.md
├── pyproject.toml                # Project config (uv)
└── .gitignore
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Summarizer page |
| GET | `/methodology` | Research methodology page |
| GET | `/about` | Model & project info |
| GET | `/health` | Health + model readiness |
| POST | `/api/summarize` | Single fine-tuned model inference |
| POST | `/api/compare` | Baseline + fine-tuned comparison |

### Request Format

```json
// Single model
POST /api/summarize
{
  "source_text": "Text to summarize...",
  "max_compression_percent": 20
}

// Comparison
POST /api/compare
{
  "source_text": "Text to summarize...",
  "max_compression_percent": 20
}
```

### Response Format

```json
{
  "max_compression_percent": 20,
  "source_word_count": 240,
  "results": [
    {
      "model_id": "finetuned",
      "model_label": "Fine-tuned FLAN-T5-small",
      "summary": "Generated summary...",
      "summary_word_count": 43,
      "actual_compression_percent": 17.92,
      "within_limit": true,
      "generation_time_ms": 156,
      "request_id": "a1b2c3d4"
    }
  ]
}
```

## Configuration

All settings via environment variables or `.env` file:

```bash
# Required
BASELINE_MODEL_PATH=./app/models/baseline
FINETUNED_MODEL_PATH=./app/models/finetuned

# Optional
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
MODEL_LOAD_STRATEGY=both          # "both" | "serialized"
DEVICE=auto                       # "auto" | "cuda" | "cpu" | "mps"
MAX_INPUT_TOKENS=512
MAX_OUTPUT_TOKENS=128
NUM_BEAMS=4
DO_SAMPLE=false
```

## Deployment

**Recommended topology:**

```
User Browser (HTTPS)
       │
Reverse Proxy (Nginx/Caddy) ── TLS termination, static files
       │
FastAPI + Uvicorn (single worker)
       ├── app/models/baseline/
       ├── app/models/finetuned/
       └── optional database
```

Key points:
- **Single worker** — both models share GPU memory; multiple workers would duplicate
- **HTTPS required** — user text in requests
- **Health endpoint** — enables load balancer readiness probes
- **CUDA preferred** — CPU fallback automatic

See `docs/design/decision-deployment.md` for full details.

## Development

### Running Tests

```bash
# All tests
uv run pytest app/tests -v

# Unit tests only
uv run pytest app/tests/test_metrics.py app/tests/test_validation.py -v

# With coverage
uv run pytest app/tests --cov=app --cov-report=term-missing
```

### Linting & Type Checking

```bash
uv run ruff check app
uv run mypy app
```

### Phase Plans

Implementation follows 6 phases from `docs/design/decision-roadmap.md`:

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1** | ✅ Complete | Project setup — FastAPI skeleton, config, templates, static, health route |
| **Phase 2** | ✅ Complete | Model integration — registry, summarizer, metrics, token validation, deterministic gen, device selection (both models loaded on CUDA) |
| **Phase 3** | ✅ Complete | Core UI — source editor, threshold selector, model mode, result cards, copy, responsive, accessible |
| **Phase 4** | ✅ Complete | Comparison — dual endpoint, paired results, partial failure handling, aligned metrics |
| **Phase 5** | ✅ Complete | Methodology & polish — methodology/about pages, design system, accessibility audit, copy confirmation |
| **Phase 6** | ⬜ Not started | Validation & deployment — tests, benchmarks, production config, HTTPS proxy |

**Blocker for Phase 2**: Export model checkpoints from Colab to `app/models/baseline/` and `app/models/finetuned/`.

Each phase has explicit exit criteria in `plans/`.

## Design System

- **Primary**: Deep navy (`#1a3a5c`)
- **Success**: Teal/green (`#0d7a3f`) — cap compliance
- **Warning**: Amber (`#b87400`) — cap exceeded
- **Error**: Red (`#c00`)
- **Spacing**: 8px base scale
- **Typography**: System sans-serif stack
- **Dark mode**: Automatic via `prefers-color-scheme`

## License

MIT License — see LICENSE file for details.

## Related Work

This web application is the demonstration interface for the research project:

> **Fine-Tuning Small Transformer Models for Information-Preserving Extreme Text Summarization**

The Colab notebook handles dataset validation, fine-tuning, and formal evaluation (blind annotation, bootstrap analysis, ROUGE-L). This application loads exported model artifacts and provides interactive inference and comparison.