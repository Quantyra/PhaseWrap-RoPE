# Story template

## Story ID and title
S092 - Synthetic score-vs-offset diagnostics

## User value
As a research lead, I want one final mechanism-level diagnostic on the synthetic family, so we can decide whether the salvage path has any remaining technical value or should be paused.

## Acceptance criteria
- Score-vs-offset diagnostics are produced for `V0` and `V3`
- The result states whether `V3` shows a clearer relative-offset structure than `V0`
- The salvage path is either paused or justified for one more step

## Outputs
- `docs/research/`
- `logs/diagnostics/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-first-synthetic-packet-v1.md`
- `logs/ablation_runs/synthetic-v0-s42/metrics.json`
- `logs/ablation_runs/synthetic-v3-s42/metrics.json`

## Out of scope
- Remote execution
- New variants
- Broad synthetic expansion

## Dependencies
- S091

## Risks
- The diagnostics may confirm there is no meaningful relative-offset advantage, in which case the salvage path should be paused again.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-07 09:02 (Pacific/Honolulu)
