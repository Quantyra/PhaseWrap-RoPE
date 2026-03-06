# Story template

## Story ID and title
S054 - V4 robust local calibration protocol

## User value
As a research lead, I want a more robust local calibration protocol for `V4`, so the active track can be judged without overfitting to a brittle threshold rule.

## Acceptance criteria
- A preferred local calibration protocol is specified
- The protocol is justified against the current threshold-sweep evidence
- The next zero-credit validation packet is defined

## Outputs
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-v4-local-threshold-calibration-investigation-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S053

## Risks
- A more robust calibration protocol may still fail to remove the imdb blocker.

## Unit tests (development stories only)
- None unless code changes begin here.

## Cycle time
- Start: 2026-03-06 13:27 (Pacific/Honolulu)

## Notes
- Keep this step zero-credit.
