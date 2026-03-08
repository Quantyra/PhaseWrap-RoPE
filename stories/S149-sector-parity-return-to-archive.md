# Story template

## Story ID and title
S149 - Sector-parity return to archive

## User value
As a research lead, I want the sector-parity restart formally returned to archive posture, so the repo closes the negative restart cleanly and preserves the artifacts without reopening drift.

## Acceptance criteria
- Record the archive decision for the sector-parity branch
- Clear active implementation work from the checkpoint
- Preserve the task family and artifacts at memo/archive level

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-sector-parity-decision-memo-v1.md`
- `docs/research/q-rope-first-sector-parity-packet-v1.md`

## Out of scope
- New implementation work
- New experiments
- Remote execution

## Dependencies
- S148

## Risks
- If the branch is not formally archived, future work may misread a clean negative restart as an invitation for ad hoc tuning.

## Unit tests (development stories only)
- No new unit tests required in this memo step.

## Cycle time
- Start: 2026-03-08 10:01 (Pacific/Honolulu)
- End: 2026-03-08 10:04 (Pacific/Honolulu)
