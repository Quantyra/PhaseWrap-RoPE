# Story template

## Story ID and title
S128 - Pair-state implementation plan

## User value
As a research lead, I want the approved pair-state restart translated into a minimal implementation plan, so the new phase can execute without reopening broader scope.

## Acceptance criteria
- Exact files to change are listed
- Exact diagnostics and tests are listed
- The implementation remains confined to the approved synthetic packet

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-pair-state-restart-brief-draft-v1.md`
- `docs/research/q-rope-pair-state-approval-gate-v1.md`

## Out of scope
- Remote execution
- Benchmark expansion
- Code changes in this step

## Dependencies
- S127

## Risks
- If the implementation plan is loose, the approved restart can still sprawl into another unbounded branch.

## Unit tests (development stories only)
- No new unit tests required in this planning step.

## Cycle time
- Start: 2026-03-07 18:19 (Pacific/Honolulu)
- End: 2026-03-07 18:22 (Pacific/Honolulu)
