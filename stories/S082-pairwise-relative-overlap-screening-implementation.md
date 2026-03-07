# Story template

## Story ID and title
S082 - Pairwise relative-overlap screening implementation

## User value
As a research lead, I want the pairwise-overlap diagnostic path implemented and screened, so we can test whether a more faithful comparison primitive improves the interpretability or separation of `V3` vs `V0`.

## Acceptance criteria
- A local pairwise-overlap helper is implemented
- Focused tests are updated
- The first diagnostic packet runs for `V0` vs `V3`

## Outputs
- `src/qrope/`
- `tests/`
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-pairwise-relative-overlap-implementation-plan-v1.md`

## Out of scope
- Paid remote execution
- Benchmark/task expansion as the primary branch

## Dependencies
- S081

## Risks
- The more faithful pairwise path may still fail to create useful `V3` separation, in which case the redesign branch should be stopped quickly.

## Unit tests (development stories only)
- Add or update focused coverage as needed.

## Cycle time
- Start: 2026-03-06 14:40 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:43 (Pacific/Honolulu)
- Decision: `NO-GO`. The first pairwise-overlap diagnostic path did not separate `V3` from `V0` and failed the redesign promotion gate.
