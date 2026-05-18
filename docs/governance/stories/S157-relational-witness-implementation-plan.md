# Story template

## Story ID and title
S157 - Relational witness implementation plan

## User value
As a research lead, I want the approved relational witness restart translated into a strict implementation plan, so the repo reopens in a controlled way and does not drift beyond the first falsification packet.

## Acceptance criteria
- Define exact writable files
- Define exact diagnostics and audit outputs
- Keep scope to one candidate and one baseline

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-relational-witness-implementation-approval-gate-v1.md`
- `docs/research/q-rope-relational-witness-restart-brief-v1.md`

## Out of scope
- Writing implementation code
- Running experiments
- Remote execution

## Dependencies
- S156

## Risks
- If the plan is not tight, the witness-head restart can quietly become a generic hybrid model exercise instead of a falsifiable research test.

## Unit tests (development stories only)
- No new unit tests required in this memo step.

## Cycle time
- Start: 2026-03-08 10:44 (Pacific/Honolulu)
- End: 2026-03-08 10:50 (Pacific/Honolulu)
