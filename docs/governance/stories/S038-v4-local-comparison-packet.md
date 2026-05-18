# Story template

## Story ID and title
S038 - V4 local comparison packet

## User value
As a research lead, I want a zero-credit `V3` vs `V4` local comparison packet, so we can decide whether `V4` earns any remote budget.

## Acceptance criteria
- Local `V3` vs `V4` runs are completed on the planned datasets and seeds
- Stability metrics are summarized for the local-only packet
- A go/no-go decision is recorded for any paid remote `V4` wave

## Outputs
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-v4-local-implementation-note-v1.md`
- `docs/research/q-rope-v4-local-implementation-plan-v1.md`

## Out of scope
- Paid remote `V4` execution
- Manuscript drafting

## Dependencies
- S037

## Risks
- `V4` may reduce mean performance without materially improving stability.

## Unit tests (development stories only)
- Reuse existing local test coverage; add focused tests only if the comparison tooling changes.

## Cycle time
- Start: 2026-03-06 10:05 (Pacific/Honolulu)
- End: 2026-03-06 10:32 (Pacific/Honolulu)

## Notes
- This story stays local-first and zero-credit by design.
- Completed with a local comparison packet and a no-go decision for paid remote `V4` execution in its current form.
