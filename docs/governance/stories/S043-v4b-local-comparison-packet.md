# Story template

## Story ID and title
S043 - V4b local comparison packet

## User value
As a research lead, I want a zero-credit `V3` vs `V4` vs `V4b` local packet, so we can judge whether `V4b` actually improves the stability story before any remote budget is considered.

## Acceptance criteria
- Local comparison runs are completed on the planned datasets and seeds
- Stability metrics are summarized for `V3`, `V4`, and `V4b`
- A go/no-go decision is recorded for any future remote `V4b` wave

## Outputs
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-v4b-local-implementation-note-v1.md`
- `docs/research/q-rope-v4b-local-implementation-plan-v1.md`

## Out of scope
- Paid remote execution
- Manuscript drafting

## Dependencies
- S042

## Risks
- `V4b` may still fail the local gate even if it is better than damped-only `V4`.

## Unit tests (development stories only)
- Reuse existing coverage unless comparison tooling changes.

## Cycle time
- Start: 2026-03-06 11:28 (Pacific/Honolulu)
- End: 2026-03-06 11:45 (Pacific/Honolulu)

## Notes
- Keep this step zero-credit and variant-sensitive.
- Completed with a provisional local packet and a hold decision due to process-level nondeterminism in the current local statevector path.
