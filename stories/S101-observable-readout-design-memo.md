# Story template

## Story ID and title
S101 - Observable/readout design memo

## User value
As a research lead, I want the proposed mechanism to have a named observable with a concrete discrimination argument, so future work does not fall back into ambiguous score-shift behavior.

## Acceptance criteria
- One observable is specified
- Its discrimination argument is explicit
- No implementation is opened

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-explicit-interference-proposal-hardening-v1.md`

## Out of scope
- Code changes
- Experiments

## Dependencies
- S100

## Risks
- If the observable argument is weak, the mechanism proposal will fail before implementation.

## Unit tests (development stories only)
- No new unit tests required.

## Cycle time
- Start: 2026-03-07 10:20 (Pacific/Honolulu)
- End: 2026-03-07 10:27 (Pacific/Honolulu)
