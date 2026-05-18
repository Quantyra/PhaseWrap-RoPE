# Story template

## Story ID and title
S058 - V3 token-to-score sensitivity diagnostics

## User value
As a research lead, I want token-to-score sensitivity diagnostics on the primary local reference path, so we can determine whether a future variant needs a new phase-to-score coupling mechanism rather than more calibration work.

## Acceptance criteria
- A zero-credit diagnostic plan is defined on the local variant-sensitive backend
- The sensitivity metrics to inspect are specified
- A decision framework is recorded for whether a new mechanism-level variant is justified later

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-v3-v4-score-geometry-diagnostics-v1.md`
- `docs/research/q-rope-post-calibration-variant-reassessment-v1.md`

## Out of scope
- Paid remote execution
- Immediate new variant design

## Dependencies
- S057

## Risks
- Sensitivity diagnostics may confirm that the current local scoring path is too weakly expressive, forcing a later return to mechanism redesign.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 14:17 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:22 (Pacific/Honolulu)
- Decision: `V4` consistently compresses token-to-score sensitivity without delivering a matching discrimination gain, so future progress requires mechanism-level coupling analysis rather than more calibration work.
