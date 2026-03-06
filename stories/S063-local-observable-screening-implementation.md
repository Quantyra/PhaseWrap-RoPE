# Story template

## Story ID and title
S063 - Local observable screening implementation

## User value
As a research lead, I want the local observable screening path implemented, so we can test `q2` and `parity` against the current weighted readout without confusing that work with a new variant branch.

## Acceptance criteria
- Local readout selection is implemented
- Focused test coverage is updated
- A zero-credit screening packet can be run with `weighted`, `q2`, and `parity`

## Outputs
- `src/qrope/`
- `tests/`
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-local-observable-screening-implementation-plan-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S062

## Risks
- The screening-path implementation may confirm that local observable upgrades help infrastructure quality but still do not justify any variant-level change.

## Unit tests (development stories only)
- Add or update focused coverage as needed.

## Cycle time
- Start: 2026-03-06 14:44 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:53 (Pacific/Honolulu)
- Decision: `q2` is a `NO-GO`; `parity` is the only viable local screening-path upgrade candidate and should be evaluated further before any broader redesign decision.
