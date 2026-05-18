# Story template

## Story ID and title
S024 - Remote wave-2 variant expansion

## User value
As a research lead, I want the matched remote evidence expanded beyond `V0` and `V3`, so the supplemental comparator story is less vulnerable to cherry-picking concerns.

## Acceptance criteria
- At least one additional intermediate variant (`V1` or `V2`) is executed on both remote backends for the fixed slice.
- Remote evidence note is updated with the expanded comparator set.
- Costs and latency are tracked for the added runs.

## Outputs
- `logs/ablation_runs/`
- `docs/research/`

## Evidence and references
- `docs/research/q-rope-matched-remote-supplemental-note-v1.md`

## Out of scope
- Full all-dataset remote matrix
- Manuscript drafting

## Dependencies
- S023

## Risks
- Additional remote runs may add cost/latency without materially changing the directional conclusion.

## Unit tests (development stories only)
- n/a unless code changes are required.

## Cycle time
- Start: 2026-03-06 05:50 (Pacific/Honolulu)
- End: 2026-03-06 06:16 (Pacific/Honolulu)
- Total: 00:26

## Notes
- Completed with `V2` executed on both remote backends for the matched Yelp slice.
- Result exposed backend asymmetry: Quandela `V2` matched `V3` on accuracy, while IBM `V2` matched `V0`.
- This reduces cherry-picking risk and justifies a seed-expansion story rather than stronger claims.
