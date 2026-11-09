# Decision: Roadmap — Phased Implementation Plan

## Context
The design document (section 13) defines 6 implementation phases for the Extreme Text Summarization Web Application. This decision records the phases, their exit criteria, and dependencies to serve as the project roadmap.

## Decision
Implement the project in 6 sequential phases as defined in the design document, with explicit exit criteria for each phase. No phase begins until the previous phase's exit criteria are verified.

## Phases

### Phase 1: Project Setup
**Goal**: Running FastAPI skeleton with config, templates, static dirs, health route.
**Exit Criteria**:
- `uv run uvicorn app.main:app --reload` starts without errors
- `GET /` returns HTML (Jinja2 template)
- `GET /health` returns JSON with model readiness fields
- `GET /methodology` and `GET /about` return HTML pages
- Static assets served from `/static/`
- Configuration via Pydantic Settings

### Phase 2: Model Integration
**Goal**: Working inference service with both checkpoints loaded.
**Exit Criteria**:
- ModelRegistry loads baseline and fine-tuned checkpoints at startup
- Summarizer service generates summaries with correct prompt format
- Metrics service calculates word count, compression ratio, cap compliance
- Token limit validation (512 tokens) rejects/validates explicitly
- Deterministic generation config (num_beams=4, do_sample=False)
- Device auto-selection (CUDA preferred, CPU fallback)

### Phase 3: Core UI
**Goal**: Single-model summarization page with all interactive components.
**Exit Criteria**:
- Source text editor with live word count
- Threshold selector (10%/20%/30% segmented buttons)
- Model mode selector (fine-tuned only / compare)
- Generate button with loading state
- Result card: model label, summary, word counts, compression ratio, cap status
- Error states displayed user-readably
- Copy-to-clipboard for summary
- Responsive layout (mobile stacks, desktop side-by-side)
- Accessibility: semantic HTML, keyboard operable, focus rings, labels

### Phase 4: Comparison
**Goal**: Side-by-side baseline vs fine-tuned comparison.
**Exit Criteria**:
- POST /api/compare returns both model results for same input/threshold
- Comparison view shows two aligned result cards
- Partial failure handling: shows successful result + error state for failed model
- Metrics visually aligned for direct comparison

### Phase 5: Methodology and Polish
**Goal**: Presentation-ready web application.
**Exit Criteria**:
- Methodology page with research question, models, compression limits, evaluation, limitations
- About page with model checkpoint labels, version metadata
- Responsive styles polished (design system from decision-ui-design.md)
- Accessibility audit: keyboard navigation, screen-reader announcements, contrast
- Copy action confirmation state
- No console errors in browser

### Phase 6: Validation and Deployment
**Goal**: Deployable MVP.
**Exit Criteria**:
- All test suites pass (unit, service, API, UI)
- Inference latency benchmarked on target hardware
- Cold-start model load time measured
- Memory usage documented
- Production server config (Uvicorn single worker)
- HTTPS reverse proxy config (Nginx/Caddy)
- Health endpoint exposes model readiness for load balancer

## Consequences
- Clear phase gates prevent scope creep
- Each phase delivers verifiable functionality
- Dependencies are explicit (Phase 2 requires Phase 1, etc.)
- Rollback is trivial per phase (git revert)

## Alternatives Considered
- **Parallel phases**: Rejected — model integration (Phase 2) is prerequisite for UI (Phase 3)
- **Combined Phase 1+2**: Rejected — separates infrastructure from ML complexity
- **Skipping Phase 5**: Rejected — methodology page is core to research transparency

## Status
**Accepted** — Implementation progress:

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Project Setup | ✅ Complete | All exit criteria verified |
| Phase 2: Model Integration | 🟡 Code complete, needs checkpoints | ModelRegistry, Summarizer, Metrics, token validation, deterministic gen, device selection implemented; blocked on Colab checkpoint export |
| Phase 3: Core UI | ✅ Complete | Source editor, threshold selector, model mode, result cards, copy, responsive, accessible |
| Phase 4: Comparison | ✅ Complete | Dual endpoint, paired results, partial failure handling, aligned metrics |
| Phase 5: Methodology & Polish | ✅ Complete | Methodology/about pages, design system, accessibility audit, copy confirmation |
| Phase 6: Validation & Deployment | ⬜ Not started | Tests, benchmarks, production config, HTTPS proxy |

## Implementation Notes
- Phase plans created in `plans/phase-N-<name>.md`
- Each phase references relevant decision files
- Exit criteria are testable/observable
- Decision files updated as implementation reveals new choices