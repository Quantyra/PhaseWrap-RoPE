# Story template

## Story ID and title
S129 - Pair-state implementation

## User value
As a research lead, I want the approved pair-state restart implemented inside the fixed local synthetic scope, so the new mechanism can be falsified cleanly.

## Acceptance criteria
- `V_pairstate_relational` is implemented locally
- required diagnostics and focused tests are added
- only the fixed synthetic packet scope is touched

## Outputs
- `src/qrope/`
- `tests/`
- `logs/ablation_runs/`
- `logs/diagnostics/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-pairstate-implementation-plan-v1.md`
- `docs/research/q-rope-pair-state-approval-gate-v1.md`

## Out of scope
- Remote execution
- Benchmark expansion
- Additional pair-state branches

## Dependencies
- S128

## Risks
- If the implementation violates sector-first measurement ordering, the branch should be treated as invalid rather than “partially working.”

## Unit tests (development stories only)
- Add the focused tests defined in the implementation plan.

## Cycle time
- Start: 2026-03-07 18:22 (Pacific/Honolulu)
