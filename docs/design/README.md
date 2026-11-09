# Design Decisions Index — essenza

This directory contains **one file per design decision** for essenza (Extreme Text Summarization Web Application). Each decision is self-contained and traceable to implementation.

## Decision Files

| File | Decision Area | Status |
|------|---------------|--------|
| `decision-model-registry.md` | Model loading, caching, device selection, readiness | 🔴 Phase 2 |
| `decision-generation-config.md` | Prompt template, token limits, decoding params, deterministic gen | 🔴 Phase 2 |
| `decision-word-count.md` | Word-count convention matching notebook; token validation | 🔴 Phase 2 |
| `decision-api-contracts.md` | Request/response schemas, error format, health endpoint | 🔴 Phase 1-2 |
| `decision-ui-design.md` | Design system, layout, responsive behavior, accessibility | 🔴 Phase 3 |
| `decision-comparison-mode.md` | Side-by-side endpoint, partial failure handling | 🔴 Phase 4 |
| `decision-deployment.md` | Production server, workers, CUDA/CPU, HTTPS, reverse proxy | 🟡 Phase 6 |
| `decision-testing.md` | Test layers, fixtures, research consistency checks | 🔴 Phase 1+ |
| `decision-roadmap.md` | Phased implementation plan (6 phases) with exit criteria | 🔴 Phase 1 |
| `decision-open-questions.md` | Deferred decisions | 🟡 Create as needed |
| `decision-risks.md` | Identified risks & mitigations | 🟡 Create as needed |
| `decision-<topic>.md` | Additional domain-specific decisions | 🟢 Add during implementation |

**Legend**: 🔴 Required for all projects | 🟡 Conditional | 🟢 As-needed

## Convention

- **One decision per file** — named `decision-<short-kebab-case>.md`
- **Sections**: Context, Decision, Consequences, Alternatives Considered, Status, Implementation Notes
- **Update existing file** when implementation changes a decision
- **Add new file** when implementation introduces a new decision
- **Reference in commits**: `feat(<area>): <desc> per decision-<x>.md decision-<y>.md`

## Required First Decisions (create before/during Phase 1)

1. **Roadmap** — 6 phases with explicit exit criteria (from design doc section 13)
2. **API Contracts** — Request/response schemas, validation rules, error format
3. **Model Registry** — Loading strategy, device selection, readiness, single-load
4. **Generation Config** — Prompt format, token limits, decoding, deterministic gen
5. **Word Count Convention** — Must match Colab notebook; token validation at 512
6. **UI Design System** — Colors, spacing, typography, accessibility baseline
7. **Testing Strategy** — Unit/service/API/UI layers + research consistency

## Template

Use `decision-TEMPLATE.md` as the starting point for each new decision.

## Legacy Sources

- Original design document: `docs/design/Extreme_Text_Summarization_Web_Application_Design_Document.docx`
- This index and decision files are the **canonical current design**

---

*Created: November 09, 2026 | Project: essenza (Extreme Text Summarization Web Application)*