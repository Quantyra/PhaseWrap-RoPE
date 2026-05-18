# Story template

## Story ID and title
S099 - State-preparation design memo

## User value
As a research lead, I want the new mechanism to have an exact state-preparation design, so any future restart is grounded in a concrete branch structure rather than hand-waving.

## Acceptance criteria
- Branch `A` and branch `B` state preparation are specified
- Token and position roles are explicit
- No implementation is opened

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-explicit-relative-phase-interference-proposal-v1.md`

## Out of scope
- Code changes
- Experiments

## Dependencies
- S098

## Risks
- If state preparation remains vague, the comparator proposal will not be falsifiable.

## Unit tests (development stories only)
- No new unit tests required.

## Cycle time
- Start: 2026-03-07 10:08 (Pacific/Honolulu)
- End: 2026-03-07 10:14 (Pacific/Honolulu)
