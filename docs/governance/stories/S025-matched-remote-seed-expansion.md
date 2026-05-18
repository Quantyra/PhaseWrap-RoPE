# Story template

## Story ID and title
S025 - Matched remote seed expansion

## User value
As a research lead, I want the matched remote packet repeated on an additional seed, so we can tell whether the current backend asymmetry is stable or a seed artifact.

## Acceptance criteria
- At least one additional seed is executed for the matched Yelp remote slice on both backends.
- The supplemental note is updated with seed-sensitivity observations.
- Costs and latency are tracked for the added runs.

## Outputs
- `logs/ablation_runs/`
- `docs/research/`

## Evidence and references
- `docs/research/q-rope-matched-remote-supplemental-note-v1.md`

## Out of scope
- Full remote matrix across all seeds and datasets
- Manuscript drafting

## Dependencies
- S024

## Risks
- Additional seed coverage may still be too small to stabilize cross-provider conclusions.

## Unit tests (development stories only)
- n/a unless code changes are required.

## Cycle time
- Start: 2026-03-06 06:17 (Pacific/Honolulu)
- End: 2026-03-06 07:04 (Pacific/Honolulu)
- Total: 00:47

## Notes
- Completed with a full matched seed `777` packet on both providers for `V0`, `V2`, and `V3`.
- IBM-only seed `123` also executed, but Quandela was blocked on seed `123` by provider-side `400` submission errors for some parameter points.
- Result: the remote picture is materially seed-sensitive and should be treated as unstable.
