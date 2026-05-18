# Story template

## Story ID and title
S037 - V4 local implementation

## User value
As a research lead, I want `V4` implemented locally, so we can test the stability-oriented variant without consuming provider credits.

## Acceptance criteria
- `V4` config exists
- `V4` phase schedule is implemented across relevant local and remote translation paths
- Local `V3` vs `V4` execution path is ready

## Outputs
- `configs/ablation/`
- `src/qrope/`
- `tests/`

## Evidence and references
- `docs/research/q-rope-v4-local-implementation-plan-v1.md`

## Out of scope
- Paid remote execution
- Manuscript drafting

## Dependencies
- S036

## Risks
- `V4` may fail locally even if the design is well-motivated.

## Unit tests (development stories only)
- Add or update focused unit coverage as needed.

## Cycle time
- Start: 2026-03-06 08:59 (Pacific/Honolulu)
- End: 2026-03-06 10:05 (Pacific/Honolulu)

## Notes
- Active next story after the `V4` local implementation plan is locked.
- Completed with a zero-credit local implementation across config, local simulation, and backend translation paths.
