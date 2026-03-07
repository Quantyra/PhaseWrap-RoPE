# Story template

## Story ID and title
S075 - Interference-tail screening implementation

## User value
As a research lead, I want the single interference-tail candidate implemented and screened, so we can test whether the broader local redesign is actually better than the current baseline tail.

## Acceptance criteria
- `mix_it1` is implemented locally
- Focused tests are updated
- The zero-credit `mix_v0` vs `mix_it1` parity packet runs

## Outputs
- `src/qrope/`
- `tests/`
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-interference-tail-screening-implementation-plan-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S074

## Risks
- Even the interference-tail candidate may still be too weak, which would indicate the local screening branch is approaching diminishing returns.

## Unit tests (development stories only)
- Add or update focused coverage as needed.

## Cycle time
- Start: 2026-03-06 14:20 (Pacific/Honolulu)
