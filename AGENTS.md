# AGENTS.md — essenza Conventions

## Project Overview
**essenza** — Extreme Text Summarization Web Application

- **Platform**: FastAPI + Jinja2 server-rendered web application (Python)
- **Model Runtime**: Hugging Face Transformers + PyTorch (FLAN-T5-small baseline + fine-tuned checkpoint)
- **Architecture**: Server-rendered pages + JSON API endpoints; model loaded once at startup
- **Docs**: `docs/design/` (canonical decision records from design document)
- **Research Question**: Does additional fine-tuning improve a pretrained Transformer's ability to preserve important facts when summarizing text under maximum length limits of 10%, 20%, and 30%?

---

## Repository Structure

```
essenza/
├── app/                           # FastAPI application
│   ├── main.py                    # Application entrypoint + lifespan
│   ├── config.py                  # Environment-based configuration
│   ├── routers/
│   │   ├── pages.py               # Jinja page routes (GET /, /methodology, /about)
│   │   └── summarization.py       # POST /api/summarize, /api/compare
│   ├── schemas/
│   │   └── summarization.py       # Pydantic request/response models
│   ├── services/
│   │   ├── model_registry.py      # Load/retrieve model instances at startup
│   │   ├── summarizer.py          # Tokenization, generation, decoding
│   │   └── metrics.py             # Word count, compression ratio, cap compliance
│   ├── templates/
│   │   ├── base.html              # Base template
│   │   ├── index.html             # Summarizer page
│   │   ├── methodology.html       # Methodology page
│   │   └── about.html             # About/model info page
│   ├── static/
│   │   ├── css/styles.css
│   │   ├── js/app.js
│   │   └── img/
│   ├── models/
│   │   ├── baseline/              # Baseline model artifacts
│   │   └── finetuned/             # Fine-tuned model artifacts
│   └── tests/
│       ├── test_metrics.py
│       ├── test_validation.py
│       └── test_routes.py
├── docs/design/                   # Canonical design decisions (from design doc)
├── plans/                         # Implementation plans (one per phase)
├── AGENTS.md                      # This file
├── WORKFLOW.md                    # Agent onboarding & execution guide
├── QUICKSTART.md                  # One-page handoff checklist
├── pyproject.toml                 # Python project config
└── requirements.txt               # Dependencies
```

---

## Core Design Principles

| Principle | Description |
|-----------|-------------|
| **Server-rendered first** | FastAPI + Jinja2; minimal JS for progressive enhancement only |
| **Models loaded once** | ModelRegistry loads checkpoints at startup; reuse for all requests |
| **Deterministic generation** | Use `num_beams=4`, `do_sample=False` for reproducible demos |
| **Cap is a ceiling, not target** | Measure and report actual compression ratio; never silently truncate |
| **Research honesty** | UI must not imply word cap guarantees factual correctness |
| **Notebook boundary** | Training/fine-tuning stays in Colab; web app consumes exported checkpoints only |

---

## Development Workflow

1. **Review design decisions** — Check `docs/design/` and the design document before implementing
2. **Record each decision** — One file per decision under `docs/design/` (see `decision-TEMPLATE.md`)
3. **Create phase plan** — Write detailed plan in `plans/phase-N-<name>.md` (6 phases in design doc)
4. **Confirm before implementing** — Ask "Start implementing?" — only proceed on explicit confirmation
5. **Implement** — Follow the implementation order below
6. **Test** — Unit tests for metrics/validation, service tests for model loading, API tests for routes
7. **Update decisions** — Edit existing decision file if implementation changes it; add new file for new decisions

### Decision Record Convention
- File naming: `docs/design/decision-<short-kebab-case>.md`
- One decision per file
- Include: Context, Decision, Consequences, Alternatives Considered, Status, Implementation Notes

---

## Implementation Order (from Design Doc Phases)

1. **Phase 1: Project setup** — FastAPI app, config, templates, static dirs, health route
2. **Phase 2: Model integration** — Export model artifacts, implement ModelRegistry and Summarizer, verify checkpoints
3. **Phase 3: Core UI** — Source editor, threshold selector, model mode, result cards, loading/error states
4. **Phase 4: Comparison** — Compare endpoint and paired result display
5. **Phase 5: Methodology and polish** — Methodology/about pages, responsive styles, accessibility, copy action
6. **Phase 6: Validation and deployment** — Run tests, benchmark inference, configure production server + HTTPS

---

## Code Conventions

### Python
- **Type hints everywhere** — Pydantic for request/response schemas, `typing` for internals
- **Service layer separation** — Routes delegate to services; no business logic in routes
- **Structured errors** — Error codes with field-level details; user-readable messages
- **UTC timestamps** — Store UTC, ISO format in responses
- **Tests** — `pytest`. Unit for metrics/validation. Service for model loading. API for routes.

### FastAPI / API Design
- **Request validation** — Pydantic models with strict constraints (only 10/20/30 for threshold)
- **Response contracts** — Defined in `schemas/summarization.py`; include request ID for log correlation
- **Health endpoint** — `/health` returns model readiness; no secrets or filesystem paths
- **Input limits** — 512 tokens max (matching notebook); reject/validate explicitly, never silent truncation

### Frontend (Jinja2 + Vanilla JS)
- **Semantic HTML** — Accessible by default; keyboard-operable; visible focus rings
- **Progressive enhancement** — Works without JS; JS adds async submission, copy, loading states
- **Responsive** — Single-column layout; comparison cards stack on mobile
- **Design system** — Minimal academic style; navy primary; teal/green for compliance; amber/red for overshoot

---

## Configuration & Secrets

- **Settings in `config.py`** via Pydantic Settings (environment variables)
- **Model paths configurable** — `BASELINE_MODEL_PATH`, `FINETUNED_MODEL_PATH`
- **Device selection** — Auto CUDA if available; CPU fallback; expose in health
- **Secrets** — Never in logs, exports, or responses; use environment variables only

---

## Testing Requirements

| Layer | Requirements |
|-------|--------------|
| **Metrics** | Word counting, compression ratio, allowed thresholds, prompt construction, cap compliance |
| **Validation** | Non-empty input, allowed threshold, max request size, token length limit |
| **Services** | Tokenizer input limits, model loading, deterministic generation config, device selection |
| **API** | Valid request, empty text, invalid percentage, over-limit input, model unavailable, compare response shape |
| **UI** | Responsive layout, selector behavior, loading state, error state, copy button, keyboard navigation |
| **Research consistency** | Prompt format and threshold semantics match Colab notebook; word counts use same convention |

---

## Non-Functional Requirements (from Design Doc)

- **Performance**: Target responsive inference on configured host; measure latency on actual CPU/GPU
- **Reliability**: Model readiness checked at startup; unavailable models reported clearly
- **Security**: Validate input server-side; limit request size; escape rendered user text; HTTPS in deployment
- **Privacy**: Do not save source text or summaries by default; avoid logging full user-provided text
- **Accessibility**: Semantic HTML, keyboard support, focus states, labels, screen-reader announcements
- **Maintainability**: Separate routes, schemas, model runtime, metrics, templates; configurable model identifiers
- **Reproducibility**: Expose checkpoint/version labels; record generation config in logs/metadata
- **Portability**: Support CPU-only operation; prefer CUDA where available

---

## Error Handling (from Design Doc)

| Condition | Expected Behavior |
|-----------|-------------------|
| Empty source text | Do not submit; inline validation message |
| Unsupported threshold | HTTP 422; only 10, 20, 30 valid |
| Input exceeds token limit | Clear validation error or explicit confirmation; never silent truncation |
| Model unavailable | Controlled service error; show which model unavailable |
| Generation timeout | Timeout message + retry; no partial output as complete |
| Output exceeds cap | Show summary + overshoot warning with actual ratio; no silent clipping |
| Comparison partially fails | Show successful result + clear error state for failed model |
| Very short source | Warn extreme compression impractical; ratio sensitive to small word-count changes |

---

## Git / Commits

- Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`
- Reference decision file when changing behavior (e.g., `feat(api): per decision-model-registry.md`)

---

## References

- `docs/design/` — Canonical decision records (one file per decision)
- `WORKFLOW.md` — Agent onboarding & execution guide
- `QUICKSTART.md` — One-page handoff checklist
- Design document: `docs/design/Extreme_Text_Summarization_Web_Application_Design_Document.docx`