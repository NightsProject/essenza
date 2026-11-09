# AGENTS.md — essenza Conventions

## Project Overview
**essenza** — A new project

- **Platform**: Hermes Agent plugin (Python-based, runs within Hermes plugin runtime)
- **Persistence**: SQLite initially with replaceable persistence abstraction
- **Architecture**: Plugin adapter → Application services → Domain layer → Persistence → Scheduler + Notification dispatcher
- **Docs**: `docs/design/` (canonical decision records)

---

## Repository Structure

```
essenza/
├── docs/design/                   # Canonical design decisions (one file per decision)
├── plans/                         # Implementation plans (one per phase)
├── src/                           # Plugin source
│   ├── plugin/                    # Hermes plugin adapter (tools, registration)
│   ├── services/                  # Application services (use cases)
│   ├── domain/                    # Domain entities, value objects, business rules
│   ├── persistence/               # Repository interfaces + SQLite implementation
│   ├── scheduler/                 # Background scheduler (if needed)
│   ├── notifications/             # Notification dispatcher (if needed)
│   └── config/                    # Settings, secrets, health
├── tests/                         # Unit + integration tests
├── AGENTS.md                      # This file
├── WORKFLOW.md                    # Agent onboarding & execution guide
├── QUICKSTART.md                  # One-page handoff checklist
└── pyproject.toml                 # Python project config (when created)
```

---

## Core Design Principles

| Principle | Description |
|-----------|-------------|
| **Hermes is the conversational host** | The plugin is the system of record; no model inference in the plugin |
| **Background work is independent** | Scheduled work does not depend on conversational tool calls or agent availability |
| **Persist before acknowledging** | All writes pass through domain validation; durable records before success responses |
| **Replaceable interfaces** | Storage and notification providers behind abstractions (SQLite → PostgreSQL, Hermes → email) |
| **Idempotency & stable IDs** | Prevent duplicate operations and notifications; use stable identifiers (ULIDs) |
| **Soft deletion / archival** | Retain auditability and recovery where needed |

---

## Development Workflow

1. **Review design decisions** — Check `docs/design/` before implementing any feature
2. **Record each decision** — One file per decision under `docs/design/` (see `decision-TEMPLATE.md`)
3. **Create phase plan** — Write detailed plan in `plans/phase-N-<name>.md`
4. **Confirm before implementing** — Ask "Start implementing?" — only proceed on explicit confirmation
5. **Implement** — Follow the plugin architecture layers
6. **Test** — Unit tests for domain logic, integration tests for tool registration and persistence
7. **Update decisions** — Edit existing decision file if implementation changes it; add new file for new decisions

### Decision Record Convention
- File naming: `docs/design/decision-<short-kebab-case>.md`
- One decision per file
- Include: Context, Decision, Consequences, Alternatives Considered, Status, Implementation Notes

---

## Architecture Layers (Implementation Order)

1. **Persistence layer** — SQLite schema, repository interfaces, migrations
2. **Domain layer** — Entities, value objects, business rules
3. **Application services** — Use cases
4. **Plugin adapter** — Hermes tool registration, input validation, result formatting
5. **Scheduler** — Background worker (if needed)
6. **Notifications** — Delivery, retry, fallback (if needed)
7. **Configuration** — Settings, secrets, health, diagnostics

---

## Code Conventions

### Python
- **Type hints everywhere** — Pydantic for tool schemas, `typing` for internals
- **Repository pattern** — Persistence behind interfaces; SQLite swappable for PostgreSQL
- **Structured errors** — Error codes with field-level details, not plain strings
- **Idempotency keys** — Required on mutating operations that may retry
- **UTC timestamps + IANA timezone** — Store UTC, retain timezone for display/recurrence
- **Tests** — `pytest`. Unit tests for domain. Integration for tool flows.

### Hermes Plugin Interface
- Tool names/descriptions unambiguous, inputs schema-constrained
- Results concise and structured for agent consumption
- Confirmation required for destructive actions
- Clarify ambiguous requests; never invent dates/times/recurrence rules
- Idempotency keys on retryable writes
- No internal IDs, secrets, or raw provider errors in responses

---

## Configuration & Secrets

- **Settings in config**, **secrets in host secret store** — Never plaintext in logs or exports
- Timezone (IANA) required at setup if applicable
- Secrets accessed via Hermes plugin secret mechanism only

---

## Testing Requirements

| Layer | Requirements |
|-------|--------------|
| **Domain** | Business logic, validation, determinism, edge cases |
| **Services** | CRUD lifecycles, state transitions, validation rules, soft delete |
| **Scheduler** | Due work identification, restart recovery, duplicate prevention (if applicable) |
| **Notifications** | Delivery, retry/backoff, fallback, duplicate prevention (if applicable) |
| **Tools** | Schema validation, confirmation flows, error responses, scope enforcement |
| **Architecture** | Layer boundary enforcement (no invalid imports) |

---

## Non-Functional Requirements

- **Performance**: Local reads/writes immediate; expensive queries bounded
- **Reliability**: Critical state survives plugin/host restarts
- **Correctness**: Date/time/timezone handling deterministic and tested
- **Maintainability**: Clear layer separation
- **Observability**: Health, pending work, retry counts, recent failures exposed
- **Privacy**: Data local by default; transmit only what's needed for notifications

---

## Git / Commits

- Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`
- Reference decision file when changing behavior (e.g., `feat(scheduler): per decision-scheduler.md`)

---

## References

- `docs/design/` — Canonical decision records (one file per decision)
- `WORKFLOW.md` — Agent onboarding & execution guide
- `QUICKSTART.md` — One-page handoff checklist