# Story template

## Story ID and title
S048 - Local screening circuit implementation

## User value
As a research lead, I want the redesigned local screening circuit implemented, so the local gate can be tested for actual variant discriminability.

## Acceptance criteria
- The redesigned local circuit is implemented
- The richer all-qubit score path is implemented
- Focused tests pass
- The deterministic packet can be rerun on the new local screening gate

## Outputs
- `src/qrope/`
- `tests/`
- `docs/research/`

## Evidence and references
- `docs/research/q-rope-local-screening-circuit-implementation-plan-v1.md`

## Out of scope
- Paid remote execution
- Remote backend redesign

## Dependencies
- S047

## Risks
- The upgraded local circuit may still not separate variants enough to support promotion decisions.

## Unit tests (development stories only)
- Add or update focused tests as needed.

## Cycle time
- Start: 2026-03-06 12:28 (Pacific/Honolulu)
- End: 2026-03-06 12:40 (Pacific/Honolulu)

## Notes
- Keep this step zero-credit.
- Completed with a redesigned local screening circuit, richer all-qubit score path, focused tests, and a local smoke run.
