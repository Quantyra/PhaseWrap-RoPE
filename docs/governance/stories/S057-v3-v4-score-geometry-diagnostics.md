# Story template

## Story ID and title
S057 - V3 vs V4 score-geometry diagnostics

## User value
As a research lead, I want score-level diagnostics for `V3` and `V4`, so we can determine whether `V4` has a recoverable calibration/geometry issue or should remain exploratory until a new variant mechanism is proposed.

## Acceptance criteria
- A zero-credit diagnostic packet is defined on the variant-sensitive local backend
- Score-geometry metrics are specified
- A decision framework is recorded for whether `V4` remains worth local refinement

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-post-calibration-variant-reassessment-v1.md`
- `docs/research/q-rope-v4-robust-calibration-local-implementation-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S056

## Risks
- Diagnostics may show that the current `V4` branch has no meaningful path forward without a new mechanism.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 14:10 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:17 (Pacific/Honolulu)
- Decision: `V4` remains exploratory only; the score-geometry diagnostics do not support further threshold-only refinement or any remote `V4` spend.
