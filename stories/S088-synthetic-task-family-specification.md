# Story template

## Story ID and title
S088 - Synthetic task family specification

## User value
As a research lead, I want the first synthetic theorem-validation dataset family specified precisely, so the salvage restart can be executed reproducibly and interpreted causally.

## Acceptance criteria
- The first synthetic task family is specified concretely
- Generation controls and leakage checks are defined
- The first restart packet can be implemented without reopening benchmark sprawl

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-synthetic-theorem-to-mechanism-plan-v1.md`
- `docs/research/q-rope-formalization-v1.md`

## Out of scope
- Remote execution
- Broad benchmark expansion
- New variant creation

## Dependencies
- S087

## Risks
- A poorly specified synthetic family could reintroduce leakage and fail to test the theorem target cleanly.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 15:37 (Pacific/Honolulu)
