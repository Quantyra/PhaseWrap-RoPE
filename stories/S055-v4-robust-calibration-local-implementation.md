# Story template

## Story ID and title
S055 - V4 robust calibration local implementation

## User value
As a research lead, I want the robust local calibration protocol implemented for `V4`, so we can decide whether the imdb blocker survives under a stable evaluation rule.

## Acceptance criteria
- The chosen local calibration protocol is implemented
- A zero-credit local rerun packet is defined for `V4` vs `V3`
- A decision is recorded on whether calibration stabilizes the active `V4` track

## Outputs
- `src/qrope/`
- `tests/`
- `docs/research/`

## Evidence and references
- `docs/research/q-rope-v4-robust-local-calibration-protocol-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S054

## Risks
- Even the robust protocol may fail to fix the imdb blocker, forcing a later return to new-variant design.

## Unit tests (development stories only)
- Add or update focused coverage as needed.

## Cycle time
- Start: 2026-03-06 13:34 (Pacific/Honolulu)

## Notes
- Keep this step zero-credit.

## Completion
- Completed: 2026-03-06 14:04 (Pacific/Honolulu)
- Decision: robust calibration removed the earlier `imdb`-specific `V4` regression signal, but `V4` still does not justify remote promotion and no longer shows a clean advantage over `V3`.
