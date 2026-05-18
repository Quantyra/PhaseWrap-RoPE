# Story template

## Story ID and title
S107 - V_new explicit interference implementation

## User value
As a research lead, I want the approved restart mechanism implemented within the bounded synthetic-only scope, so the new restart phase can be falsified cleanly.

## Acceptance criteria
- `V_new_explicit_interference` is implemented locally
- Required tests and diagnostics are added
- Only the fixed synthetic packet scope is touched

## Outputs
- `src/qrope/`
- `tests/`
- `logs/diagnostics/`
- `logs/ablation_runs/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-vnew-implementation-plan-v1.md`
- `docs/research/q-rope-filled-restart-brief-v1.md`

## Out of scope
- Remote execution
- Benchmark expansion
- Additional mechanism branches

## Dependencies
- S106

## Risks
- If the implementation drifts beyond the fixed synthetic packet, the restart loses its falsifiability.

## Unit tests (development stories only)
- Add the focused tests defined in the implementation plan.

## Cycle time
- Start: 2026-03-07 11:14 (Pacific/Honolulu)
- End: 2026-03-07 14:15 (Pacific/Honolulu)
