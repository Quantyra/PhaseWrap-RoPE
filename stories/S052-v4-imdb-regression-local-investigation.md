# Story template

## Story ID and title
S052 - V4 IMDb regression local investigation

## User value
As a research lead, I want to investigate why `V4` regresses on `imdb` locally, so we can determine whether the current limitation is dataset-specific noise or a structural weakness in the variant.

## Acceptance criteria
- The `imdb` regression is characterized from existing local evidence
- A zero-credit local investigation path is defined
- A decision is recorded on whether `V4` remains the active track after that investigation

## Outputs
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-v4-vs-v3-larger-local-packet-v1.md`

## Out of scope
- Paid remote execution
- Reopening `V4b`

## Dependencies
- S051

## Risks
- The `imdb` regression may prove structural, weakening the case for `V4` as the lead branch.

## Unit tests (development stories only)
- None unless tooling changes.

## Cycle time
- Start: 2026-03-06 13:08 (Pacific/Honolulu)
- End: 2026-03-06 13:18 (Pacific/Honolulu)

## Notes
- Keep this step zero-credit.
- Completed with a calibration-focused diagnosis: the imdb regression appears tied to threshold shift under small class-separation margins.
