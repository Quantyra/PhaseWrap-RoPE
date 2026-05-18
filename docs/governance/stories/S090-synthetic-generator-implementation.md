# Story template

## Story ID and title
S090 - Synthetic generator implementation

## User value
As a research lead, I want the first synthetic restart packet implemented locally, so the salvage hypothesis can move from planning to executable evidence.

## Acceptance criteria
- Deterministic signed relative-offset generation is implemented
- The runner can execute the first synthetic packet locally
- Generator diagnostics are written with each run

## Outputs
- `src/qrope/`
- `tests/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-synthetic-generator-implementation-plan-v1.md`
- `docs/research/q-rope-synthetic-task-family-specification-v1.md`

## Out of scope
- Remote execution
- Bucket prediction
- Retrieval
- New variants

## Dependencies
- S089

## Risks
- Overloading the current text-based path could obscure whether failures come from the generator or the scoring path.

## Unit tests (development stories only)
- Add focused tests for generator determinism, label correctness, and runner integration.

## Cycle time
- Start: 2026-03-06 15:55 (Pacific/Honolulu)
- End: 2026-03-06 17:06 (Pacific/Honolulu)
