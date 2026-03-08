# Story template

## Story ID and title
S138 - Sector-parity restart scaffold

## User value
As a research lead, I want the next alignment-safe restart target tied to an explicit approval scaffold, so future work cannot reopen loosely or redefine success after the fact.

## Acceptance criteria
- Define the minimum restart scaffold for `synthetic_sector_parity_binary`
- Keep the work memo-only
- Predeclare pass and failure conditions

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-sector-parity-task-spec-v1.md`
- `docs/research/q-rope-future-restart-brief-template-v1.md`

## Out of scope
- New implementation work
- New experiments
- Restart approval

## Dependencies
- S137

## Risks
- If the sector-parity angle is not tied to a restart scaffold now, future work can reintroduce moving goalposts at approval time.

## Unit tests (development stories only)
- No new unit tests required in this memo step.

## Cycle time
- Start: 2026-03-08 09:05 (Pacific/Honolulu)
