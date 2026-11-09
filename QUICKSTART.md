# QUICKSTART.md — essenza One-Page Agent Handoff Checklist

## 🎯 First 5 Minutes
```bash
cd ~/Vault/Projects/essenza
cat AGENTS.md                              # Project conventions
cat docs/design/README.md                  # Decision map
cat docs/design/Extreme_Text_Summarization_Web_Application_Design_Document.docx  # Full design
```

## 📍 Where Am I?
- **Project**: `~/Vault/Projects/essenza/`
- **Design**: `docs/design/` (design doc + decision records)
- **Plan**: `plans/phase-N-<name>.md` (6 phases from design doc)
- **Source**: `app/` (FastAPI application)
- **Tests**: `app/tests/`

## 🔄 Current Phase Loop (6 phases from design doc)
1. **Phase 1: Project setup** — FastAPI app, config, templates, static dirs, health route
2. **Phase 2: Model integration** — Export artifacts, ModelRegistry, Summarizer, verify checkpoints
3. **Phase 3: Core UI** — Source editor, threshold selector, model mode, result cards, loading/error
4. **Phase 4: Comparison** — Compare endpoint + paired result display
5. **Phase 5: Methodology & polish** — Methodology/about pages, responsive styles, accessibility, copy
6. **Phase 6: Validation & deploy** — Tests, benchmark, production config, HTTPS

**Per phase**: Read plan → Confirm "Start implementing?" → Implement → Test → Verify exit criteria → Update decisions

## ⛔ Guardrails
| Never | Always |
|-------|--------|
| Code without decision | Trace implementation to decision file |
| Skip phase exit criteria | Run all phase tests before advancing |
| Hardcode secrets | Use environment variables / Pydantic Settings |
| Cross layer boundaries | Routes → Services → Model Runtime; no reverse imports |
| Silent deviation | Update decision file if implementation differs |
| Silent truncation | Validate 512-token limit explicitly; reject or confirm |
| Claim factual correctness | Report compression + cap compliance only |

## 📋 Key Decisions by Topic (create as needed)
| Topic | File |
|-------|------|
| Model registry & loading | `decision-model-registry.md` |
| Prompt & generation config | `decision-generation-config.md` |
| Word count convention | `decision-word-count.md` |
| API contracts | `decision-api-contracts.md` |
| UI/design system | `decision-ui-design.md` |
| Deployment & device | `decision-deployment.md` |
| Testing strategy | `decision-testing.md` |
| Risks | `decision-risks.md` |
| Open questions | `decision-open-questions.md` |

## ✅ Before Committing
- [ ] Tests pass (`pytest app/tests -v`)
- [ ] Layer boundaries respected (routes delegate to services)
- [ ] Conventional commit: `feat(<area>): <desc> per decision-<x>.md`
- [ ] Decision files updated if implementation diverged
- [ ] Plan checkboxes updated

## 🆘 Stuck?
1. Check `decision-risks.md` — known issue?
2. Check `decision-open-questions.md` — blocked on decision?
3. Re-read relevant decision file + design doc section
4. Ask user with specific question + decision reference

## 📁 File Creation Rules
- New decision → `docs/design/decision-<kebab-case>.md`
- New plan → `plans/phase-N-<name>.md`
- Source code → `app/` (routers, schemas, services, templates, static)
- Tests → `app/tests/` mirroring source structure

---

**Remember**: The design document + decisions ARE the spec. Code is just executable decisions.