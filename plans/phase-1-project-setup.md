# Phase 1: Project Setup

**Goal**: Create a running FastAPI skeleton with configuration, templates, static directories, and health route.

**Exit Criteria**:
- [ ] `uv run uvicorn app.main:app --reload` starts without errors
- [ ] `GET /` returns HTML (Jinja2 template)
- [ ] `GET /health` returns JSON with model readiness fields (initially all false)
- [ ] `GET /methodology` and `GET /about` return HTML pages
- [ ] Static assets served from `/static/`
- [ ] Configuration via Pydantic Settings (environment variables)
- [ ] Project structure matches design doc section 8.1

**Scope**:
- FastAPI app with lifespan for startup/shutdown
- Pydantic Settings config (model paths, device, host, port, log level)
- Jinja2 templates: base.html, index.html, methodology.html, about.html
- Static directories: css/, js/, img/
- Health endpoint with model readiness structure
- Basic logging configuration

**Out of Scope**:
- Model loading (Phase 2)
- Summarization endpoints (Phase 2-3)
- Actual UI components (Phase 3)
- Comparison endpoint (Phase 4)

**Relevant Decisions** (to create):
- `decision-roadmap.md` — this plan + phases 2-6
- `decision-api-contracts.md` — request/response schemas, health response
- `decision-deployment.md` — single worker, device selection, reverse proxy
- `decision-testing.md` — pytest setup, test layers

**Implementation Steps**:

1. **Create `decision-roadmap.md`** with all 6 phases and exit criteria
2. **Create `decision-api-contracts.md`** with request/response schemas
3. **Create `app/config.py`** — Pydantic Settings with all config options
4. **Create `app/main.py`** — FastAPI app, lifespan, routes inclusion, logging
5. **Create `app/routers/pages.py`** — GET /, /methodology, /about
6. **Create `app/routers/summarization.py`** — stub POST /api/summarize, /api/compare, GET /health
7. **Create `app/schemas/summarization.py`** — Pydantic models for requests/responses
8. **Create `app/services/model_registry.py`** — stub with readiness flags
9. **Create templates**: base.html, index.html, methodology.html, about.html
10. **Create static files**: css/styles.css (minimal), js/app.js (empty)
11. **Run and verify**: start server, test all routes

**Verification Commands**:
```bash
uv run uvicorn app.main:app --reload --port 8000 &
sleep 3
curl -s http://localhost:8000/health | jq
curl -s http://localhost:8000/ | head -20
curl -s http://localhost:8000/methodology | head -20
curl -s http://localhost:8000/about | head -20
```

**Risks**:
- Jinja2 template path resolution
- Static file mounting in FastAPI
- Pydantic Settings env var parsing

**Next Step**: Create decision-roadmap.md and decision-api-contracts.md, then implement config.py and main.py