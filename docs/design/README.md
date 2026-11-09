# Design Decisions Index — essenza

This directory contains **one file per design decision** for essenza. Each decision is self-contained and traceable to implementation.

## Decision Files

| File | Decision Area | Status |
|------|---------------|--------|
| `decision-product-boundary.md` | Product boundary (what we build/don't build) | 🔴 Create first |
| `decision-agent-integration.md` | Hermes integration method | 🔴 Create early |
| `decision-persistence.md` | Storage strategy | 🔴 Create early |
| `decision-data-design.md` | Entity schema & integrity | 🔴 Create early |
| `decision-scheduler.md` | Background work & restart recovery | 🟡 If needed |
| `decision-notification-fallback.md` | Delivery reliability & fallback | 🟡 If needed |
| `decision-plugin-tools.md` | Tool design, schemas, interaction rules | 🔴 Create early |
| `decision-testing.md` | Test strategy & acceptance criteria | 🔴 Create early |
| `decision-roadmap.md` | Phased implementation plan | 🔴 Create early |
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

## Required First Decisions (create before Phase 1)

1. **Product Boundary** — What the plugin does/doesn't do
2. **Agent Integration** — How it connects to Hermes (native plugin tools, no MCP)
3. **Persistence** — SQLite + abstraction, or other
4. **Data Design** — Core entities, IDs, timestamps, soft delete
5. **Plugin Tools** — Tool groups, schemas, confirmation rules, scope
6. **Testing** — Test layers, acceptance criteria as tests
7. **Roadmap** — Phased implementation with exit criteria

## Template

Use `decision-TEMPLATE.md` as the starting point for each new decision.

## Legacy Sources

- Original design documents (if any) preserved in `docs/design/legacy/`
- This index and decision files are the **canonical current design**

---

*Created: November 09, 2026 | Project: essenza*