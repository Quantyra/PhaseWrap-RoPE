# Story template

## Story ID and title
S065 - Parity-default local packet

## User value
As a research lead, I want the next local packet to run with parity as the default screening readout, so we can validate whether the promoted infrastructure path actually produces cleaner branch comparisons.

## Acceptance criteria
- The local packet is defined with parity as default readout
- Weighted remains available as a reference comparator where needed
- The next branch question is explicitly framed as local screening evidence, not remote evidence

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-parity-readout-promotion-decision-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S064

## Risks
- If parity-default screening does not materially improve comparison clarity, the local screening path may still require deeper redesign.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 14:58 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 15:03 (Pacific/Honolulu)
- Decision: parity remains the provisional default local screening readout, with weighted retained as a required reference comparator for major local branch decisions.
