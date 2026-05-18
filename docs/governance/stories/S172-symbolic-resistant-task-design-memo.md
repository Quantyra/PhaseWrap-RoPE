# Story template

## Story ID and title
S172 - Symbolic-resistant task design memo

## User value
As a research lead, I want one harder alignment-safe task defined, so the witness branch can be tested on a task that direct sector identity alone does not already solve perfectly.

## Acceptance criteria
- Define one new task family candidate
- State why sector one-hot should not solve it linearly
- Keep the scope memo-only

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-relational-witness-post-control-decision-v1.md`
- `docs/research/q-rope-relational-witness-symbolic-control-v1.md`
- `docs/research/q-rope-symbolic-resistant-task-design-v1.md`

## Out of scope
- Implementation
- Remote execution
- Multiple new task families in parallel

## Dependencies
- S171

## Risks
- If the new task is not explicitly symbolic-resistant, the branch will just recreate the same ambiguity on a fresh label rule.

## Unit tests (development stories only)
- No new unit tests required in this memo step.

## Cycle time
- Start: 2026-03-08 13:36 (Pacific/Honolulu)
- End: 2026-03-08 13:45 (Pacific/Honolulu)
