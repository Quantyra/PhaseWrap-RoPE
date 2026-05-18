# Story template

## Story ID and title
S042 - V4b local implementation

## User value
As a research lead, I want `V4b` implemented locally, so we can evaluate a more credible stability-oriented variant before any remote spend.

## Acceptance criteria
- `V4b` config exists
- shared effective-phase helpers are implemented
- local statevector path accepts `V4b`
- backend translation helpers accept `V4b`
- focused tests pass

## Outputs
- `configs/ablation/`
- `src/qrope/`
- `tests/`

## Evidence and references
- `docs/research/q-rope-v4b-local-implementation-plan-v1.md`

## Out of scope
- Paid remote execution
- Broad benchmark reruns

## Dependencies
- S041

## Risks
- Shared helper changes may expose unintended coupling between local and remote translation code.

## Unit tests (development stories only)
- Add or update focused tests as needed.

## Cycle time
- Start: 2026-03-06 11:14 (Pacific/Honolulu)
- End: 2026-03-06 11:28 (Pacific/Honolulu)

## Notes
- Keep this step zero-credit.
- Completed with shared effective-phase helpers, `V4b` config, focused tests, and a local smoke run.
