# Decision: Generate Compression Results for Every Loaded Model

## Context
The summarizer currently supports maximum summary lengths of 10%, 20%, and 30%, as well as multiple models registered at runtime. The home page should make it easy to inspect each compression level across every model that successfully loaded, and compare their compression outcomes in one place.

## Decision
The page provides two modes: Single model, where a user selects one model, and Generate all models, which runs every model reported as loaded by `/health`. Both modes generate results at the supported maximum compression levels (10%, 20%, and 30%). Requests run sequentially to avoid concurrent model-memory spikes. Results are grouped under clear model headings, and a summary table at the end reports model, source word count, maximum compression level, target word count, actual summary word count, actual compression, cap compliance, and elapsed time.

## Consequences
### Positive
- Users can choose one loaded model or run every loaded model across all three thresholds.
- Per-model section headings visually separate outputs; the final table makes source length, target words, actual summary words, actual compression, cap compliance, and elapsed time scannable.
- A failed individual generation is recorded as an error row/card and does not prevent other model/level combinations from running.

### Negative
- Runtime grows with the number of loaded models multiplied by three compression levels.
- Sequential calls take longer than parallel execution but avoid loading/inference contention.

### Neutral
- The existing single-summary and comparison APIs remain unchanged; the frontend calls the single-summary endpoint once per model and compression level.

## Alternatives Considered
| Alternative | Why Rejected |
|-------------|--------------|
| Run only one selected model at all levels | Does not satisfy the goal of showing every loaded model. |
| Run all model/level combinations concurrently | Higher risk of device-memory pressure and overlapping inference. |
| Add a new aggregate API endpoint | Unnecessary for the current three fixed levels; can be reconsidered if request orchestration moves server-side. |

## Status
Decided

## Implementation Notes
- Model list comes from `GET /health`; only entries with `loaded: true` are included.
- `app/static/js/app.js` runs the 3 × loaded-model combinations sequentially, reports overall progress, and preserves per-combination errors.
- `app/templates/index.html` provides a single-model selector, an all-loaded-model mode, and the final compression summary table with source and target word counts.
- `app/static/css/styles.css` styles model dividers, progress, and the horizontally scrollable summary table.

---

*Decision date: 2026-11-12 | Author: Jake | Related: `decision-api-contracts.md`, `decision-ui-design.md`*
