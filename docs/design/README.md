# Design Decisions Index — essenza

This directory contains **one file per design decision** for essenza (Extreme Text Summarization Web Application). Each decision is self-contained and traceable to implementation.

## Decision Files

| File | Decision Area | Status |
|------|---------------|--------|
| `decision-roadmap.md` | Phased implementation plan (6 phases) with exit criteria | ✅ Created (Phase 1) |
| `decision-api-contracts.md` | Request/response schemas, error format, health endpoint | ✅ Created (Phase 1-2) |
| `decision-deployment.md` | Production server, workers, CUDA/CPU, HTTPS, reverse proxy | ✅ Created (Phase 6) |
| `decision-testing.md` | Test layers, fixtures, research consistency checks | ✅ Created (Phase 1+) |
| `decision-model-registry.md` | Model loading, caching, device selection, readiness | ⬜ Not created — implemented inline in code |
| `decision-generation-config.md` | Prompt template, token limits, decoding params, deterministic gen | ⬜ Not created — implemented inline in code |
| `decision-word-count.md` | Word-count convention matching notebook; token validation | ⬜ Not created — implemented inline in code |
| `decision-ui-design.md` | Design system, layout, responsive behavior, accessibility | ⬜ Not created — implemented inline in CSS/JS |
| `decision-comparison-mode.md` | Side-by-side endpoint, partial failure handling | ⬜ Not created — implemented inline in code |
| `decision-open-questions.md` | Deferred decisions | 🟡 Create as needed |
| `decision-risks.md` | Identified risks & mitigations | 🟡 Create as needed |
| `decision-<topic>.md` | Additional domain-specific decisions | 🟢 Add during implementation |

**Legend**: ✅ Created | ⬜ Not created (implemented inline) | 🟡 Conditional | 🟢 As-needed

## Implementation Status by Phase

| Phase | Decisions Created | Notes |
|-------|-------------------|-------|
| **Phase 1: Project Setup** | roadmap, api-contracts, testing | All required first decisions done |
| **Phase 2: Model Integration** | — | Model registry, generation config, word count implemented in `app/services/` but not extracted to decision files |
| **Phase 3: Core UI** | — | UI design system implemented in `app/static/css/styles.css` and `app/static/js/app.js` |
| **Phase 4: Comparison** | — | Comparison mode implemented in `app/routers/summarization.py` |
| **Phase 5: Methodology & Polish** | — | Deployed via templates |
| **Phase 6: Validation & Deployment** | deployment | Deployment decision documented |

## Convention

- **One decision per file** — named `decision-<short-kebab-case>.md`
- **Sections**: Context, Decision, Consequences, Alternatives Considered, Status, Implementation Notes
- **Update existing file** when implementation changes a decision
- **Add new file** when implementation introduces a new decision
- **Reference in commits**: `feat(<area>): <desc> per decision-<x>.md decision-<y>.md`

## Required First Decisions (created before/during Phase 1)

1. **Roadmap** — 6 phases with explicit exit criteria (from design doc section 13) ✅
2. **API Contracts** — Request/response schemas, validation rules, error format ✅
3. **Model Registry** — Loading strategy, device selection, readiness, single-load ⬜ (in code)
4. **Generation Config** — Prompt format, token limits, decoding, deterministic gen ⬜ (in code)
5. **Word Count Convention** — Must match Colab notebook; token validation at 512 ⬜ (in code)
6. **UI Design System** — Colors, spacing, typography, accessibility baseline ⬜ (in CSS/JS)
7. **Testing Strategy** — Unit/service/API/UI layers + research consistency ✅

## Template

Use `decision-TEMPLATE.md` as the starting point for each new decision.

## Legacy Sources

- Original design document: `docs/design/Extreme_Text_Summarization_Web_Application_Design_Document.docx`
- Colab training notebook: `colab/FLAN_T5_Extreme_Summarization_Fine_Tuning.ipynb`
- This index and decision files are the **canonical current design**

---

*Created: November 09, 2026 | Project: essenza (Extreme Text Summarization Web Application) | Last updated: November 10, 2026*