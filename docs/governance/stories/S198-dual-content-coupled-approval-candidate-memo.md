# Story template

## Story ID and title
S198 - Dual content-coupled approval-candidate memo

## User value
As a research lead, I want the harder dual task reassessed as a possible future approval candidate, so the repo can decide whether this new task family is specific enough to justify a later implementation gate.

## Acceptance criteria
- Reassess one exact scaffold only
- Decide preserve-only vs approval-candidate posture
- Keep it memo-only

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-dual-content-coupled-restart-scaffold-v1.md`

## Out of scope
- Implementation
- Remote execution
- Multiple task families in parallel

## Dependencies
- S197

## Risks
- If the approval posture is raised too early, the repo will reopen implementation before the control story is fixed.

## Unit tests (development stories only)
- No unit tests required in this memo step.

## Cycle time
- Start: 2026-03-08 19:31 (Pacific/Honolulu)
- End: 2026-03-08 19:38 (Pacific/Honolulu)
