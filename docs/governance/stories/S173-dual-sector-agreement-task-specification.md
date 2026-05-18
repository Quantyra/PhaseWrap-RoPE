# Story template

## Story ID and title
S173 - Dual-sector agreement task specification

## User value
As a research lead, I want the new symbolic-resistant task pinned down formally, so any future implementation stays bounded and auditable.

## Acceptance criteria
- Specify one exact task schema
- Specify the allowed symbolic control
- Keep the step memo-only

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-symbolic-resistant-task-design-v1.md`
- `docs/research/q-rope-dual-sector-agreement-task-spec-v1.md`

## Out of scope
- Implementation
- Multiple task families
- Remote execution

## Dependencies
- S172

## Risks
- If the task is not formalized now, later implementation will drift and the control comparison will stop being fair.

## Unit tests (development stories only)
- No new unit tests required in this memo step.

## Cycle time
- Start: 2026-03-08 13:45 (Pacific/Honolulu)
- End: 2026-03-08 13:54 (Pacific/Honolulu)
