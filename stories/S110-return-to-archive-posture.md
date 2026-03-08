# Story template

## Story ID and title
S110 - Return to archive posture

## User value
As a research lead, I want the repo returned to an explicit paused/archive posture after the failed bounded restart, so future work cannot drift into unapproved experimentation.

## Acceptance criteria
- Record the restart stop decision
- Restore paused/archive status in checkpoint and notes
- Leave only memo-level future restart pathways

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-vnew-synthetic-decision-memo-v1.md`
- `docs/research/q-rope-final-salvage-pause-memo-v1.md`

## Out of scope
- New implementation work
- New experiments
- Remote execution

## Dependencies
- S109

## Risks
- If archive posture is not reasserted now, the project can slide back into low-value iteration.

## Unit tests (development stories only)
- No new unit tests required.

## Cycle time
- Start: 2026-03-07 14:20 (Pacific/Honolulu)
