# Story template

## Story ID and title
S049 - Rerun local screening packet on redesigned circuit

## User value
As a research lead, I want the local `V3` vs `V4` vs `V4b` packet rerun on the upgraded screening circuit, so we can determine whether the local gate is finally informative.

## Acceptance criteria
- The deterministic local packet is rerun on the redesigned screening circuit
- A fresh summary is produced
- A go/no-go decision is recorded for whether the local gate is now useful

## Outputs
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-local-screening-circuit-implementation-note-v1.md`

## Out of scope
- Paid remote execution
- Remote backend redesign

## Dependencies
- S048

## Risks
- Even the redesigned local circuit may remain non-discriminative.

## Unit tests (development stories only)
- Reuse current coverage unless comparison tooling changes.

## Cycle time
- Start: 2026-03-06 12:40 (Pacific/Honolulu)
- End: 2026-03-06 12:50 (Pacific/Honolulu)

## Notes
- Keep this step zero-credit.
- Completed with a deterministic rerun on the redesigned local screening circuit and a no-go decision for remote `V4b` promotion at this time.
