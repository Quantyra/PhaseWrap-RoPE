# Story template

## Story ID and title
S051 - V4 vs V3 larger local packet

## User value
As a research lead, I want a slightly larger zero-credit local packet focused on `V4` vs `V3`, so we can test whether the current `V4` signal survives beyond the smallest screening setup.

## Acceptance criteria
- A larger local packet scope is defined and executed
- `V4` vs `V3` stability and mean-performance deltas are summarized
- A fresh decision is recorded on whether any remote `V4` question is justified

## Outputs
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-variant-selection-memo-v1.md`

## Out of scope
- Paid remote execution
- Further `V4b` redesign

## Dependencies
- S050

## Risks
- The apparent `V4` edge may disappear under modest local scale-up.

## Unit tests (development stories only)
- Reuse current coverage unless tooling changes.

## Cycle time
- Start: 2026-03-06 12:58 (Pacific/Honolulu)
- End: 2026-03-06 13:08 (Pacific/Honolulu)

## Notes
- Keep this step zero-credit.
- Completed with a five-seed local packet and a hold decision on new remote `V4` execution.
