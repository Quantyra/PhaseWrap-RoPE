# Story template

## Story ID and title
S053 - V4 local threshold calibration investigation

## User value
As a research lead, I want to test whether better local calibration removes the current `imdb` regression for `V4`, so we can decide whether the issue is scoring quality or decision-rule quality.

## Acceptance criteria
- Alternative local threshold rules are compared for `V4` on `imdb`
- The effect on mean accuracy/F1 and variance is summarized
- A decision is recorded on whether calibration resolves the current blocker enough to keep `V4` as lead track

## Outputs
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-v4-imdb-regression-investigation-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S052

## Risks
- Calibration may help only marginally, leaving the `imdb` issue unresolved.

## Unit tests (development stories only)
- None unless code changes are made for calibration tooling.

## Cycle time
- Start: 2026-03-06 13:18 (Pacific/Honolulu)
- End: 2026-03-06 13:27 (Pacific/Honolulu)

## Notes
- Keep this step zero-credit.
- Completed with a threshold-rule sweep showing that calibration helps, but does not yet resolve the imdb blocker cleanly.
