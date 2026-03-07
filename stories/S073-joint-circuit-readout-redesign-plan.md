# Story template

## Story ID and title
S073 - Joint circuit-readout redesign plan

## User value
As a research lead, I want a narrow plan for a joint local circuit-readout redesign, so we can test a broader mechanism fix without opening multiple uncontrolled branches.

## Acceptance criteria
- A single narrowly scoped joint circuit-readout redesign family is chosen
- The plan keeps the work local, zero-credit, and `V3`-centered
- The evaluation gate is explicit before any implementation begins

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-broader-local-redesign-question-selection-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S072

## Risks
- The redesign scope could sprawl unless the implementation family is narrowed aggressively.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 14:15 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:16 (Pacific/Honolulu)
- Decision: narrow the broader redesign to a single local screening family, `interference-tail parity screening`, with an explicit promotion gate and no remote spend.
