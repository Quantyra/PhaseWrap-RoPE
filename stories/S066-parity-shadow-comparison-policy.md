# Story template

## Story ID and title
S066 - Parity shadow comparison policy

## User value
As a research lead, I want a policy for when weighted must shadow parity in local screening, so future local decisions remain disciplined while the promoted readout is still provisional.

## Acceptance criteria
- The parity-default and weighted-shadow policy is recorded
- Trigger conditions for weighted shadow comparison are specified
- The next local path is defined

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-parity-default-local-packet-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S065

## Risks
- Overusing weighted shadow comparisons could slow local iteration; underusing them could let a weak readout distort branch decisions.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 15:03 (Pacific/Honolulu)
