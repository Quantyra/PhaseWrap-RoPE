# Story template

## Story ID and title
S064 - Parity readout promotion decision

## User value
As a research lead, I want a decision on whether parity should become the default local screening readout, so future local screening evidence is generated on the strongest currently available infrastructure path.

## Acceptance criteria
- The parity results are compared against weighted across `V3` and `V4`
- A decision is recorded on default local screening readout status
- The next local path is defined

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-local-observable-screening-implementation-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S063

## Risks
- Promoting parity prematurely could hide weaknesses if it only helps a subset of the local packet.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 14:53 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:58 (Pacific/Honolulu)
- Decision: promote `parity` to provisional default local screening readout, while retaining `weighted` as the reference baseline until the next local packet confirms the upgrade.
