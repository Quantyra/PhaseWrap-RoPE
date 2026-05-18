# Story template

## Story ID and title
S091 - First synthetic packet execution

## User value
As a research lead, I want the first full synthetic salvage packet executed, so we can determine whether the theorem-to-mechanism restart shows any positive signal before further investment.

## Acceptance criteria
- `V0` and `V3` are executed on the synthetic family for seeds `42`, `123`, `777`
- Metrics and generator diagnostics are collected
- A decision note states whether the salvage signal is positive, null, or negative

## Outputs
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-synthetic-generator-implementation-v1.md`
- `docs/research/q-rope-synthetic-task-family-specification-v1.md`

## Out of scope
- Remote execution
- Bucket prediction
- Retrieval
- New variants

## Dependencies
- S090

## Risks
- The first synthetic packet may show no variant separation at all, which would materially weaken the salvage path.

## Unit tests (development stories only)
- Reuse the focused synthetic/local tests unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 17:06 (Pacific/Honolulu)
- End: 2026-03-07 09:02 (Pacific/Honolulu)
