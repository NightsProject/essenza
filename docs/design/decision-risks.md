# Decision: Risks and Mitigations — {{PROJECT_NAME}}

## Context
Identified risks that could impact delivery, correctness, or operations. Each risk has a concrete mitigation strategy.

## Risks

| Risk | Impact | Mitigation | Owner / Phase |
|------|--------|------------|---------------|
| {{Risk 1}} | {{High/Med/Low}} | {{Specific mitigation steps}} | {{Phase N}} |
| {{Risk 2}} | {{High/Med/Low}} | {{Specific mitigation steps}} | {{Phase N}} |
| {{Risk 3}} | {{High/Med/Low}} | {{Specific mitigation steps}} | {{Phase N}} |

## Common Hermes Plugin Risks (review each project)

| Risk | Impact | Mitigation | When to Address |
|------|--------|------------|-----------------|
| Hermes plugin runtime lacks persistent background worker | Background jobs stop on agent exit | 1. Use supervised subprocess in plugin package<br>2. Use runtime background tasks if supported<br>3. Document external service manager fallback | Phase with scheduler |
| Ambiguous natural-language inputs | Incorrect data/operations | 1. Tool schemas require explicit values<br>2. Agent resolves natural language<br>3. Always confirm interpreted values in response | Phase 1 (tools) |
| Timezone/date edge cases | Missed/duplicate occurrences | 1. Use `zoneinfo`/`dateutil` for IANA tzdata<br>2. Property-based tests for DST, month-end<br>3. Configurable policies for ambiguous times | Phase with dates/recurrence |
| Notification provider accepts but user doesn't receive | False delivery confidence | 1. Track provider acceptance ≠ user receipt<br>2. Surface "accepted by provider" not "delivered"<br>3. Delivery state machine distinguishes both | Phase with notifications |
| Concurrent background workers | Duplicate work | 1. Atomic claim (UPDATE ... RETURNING)<br>2. Unique constraint on work identity<br>3. Idempotent dispatch<br>4. Single-worker lock (DB advisory/file) | Phase with scheduler |
| Plugin update / host restart | Lost in-memory state | 1. Reconstruct all work from persistent records<br>2. Checkpoint persisted every 30s<br>3. Graceful shutdown flushes checkpoint | Phase with scheduler |
| SQLite locking under concurrency | Write failures | 1. WAL mode + connection pooling<br>2. Retry with exponential backoff<br>3. Short transactions | Phase 1 (persistence) |
| Large data set performance | Slow queries | 1. Bounded horizons / pagination<br>2. Indexes on query patterns<br>3. Lazy expansion for recurrence | Phase with planning/queries |

## Implementation-Discovered Risks (add as found)

| Risk | Discovered | Mitigation | Status |
|------|------------|------------|--------|
| {{Risk}} | {{Phase/Date}} | {{Mitigation}} | {{Planned/Implemented/Verified}} |

## Convention
- Review this file at start of each phase
- Add new risks as discovered during implementation
- Each mitigation must have a test case
- Update status as mitigations are implemented/verified
- Document runbook entries for operational risks