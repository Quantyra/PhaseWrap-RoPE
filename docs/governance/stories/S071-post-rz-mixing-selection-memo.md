# Story template

## Story ID and title
S071 - Post-RZ mixing selection memo

## User value
As a research lead, I want the post-`RZ` mixing screen translated into a clear selection memo, so we can decide whether to retain, refine, or stop this local mechanism branch.

## Acceptance criteria
- The `mix_v0`, `mix_v1`, and `mix_v2` outcomes are synthesized into a single decision memo
- The parity result and weighted shadow are reconciled explicitly
- The next mechanism step is selected without opening remote spend

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-post-rz-mixing-screening-implementation-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S070

## Risks
- The memo may conclude that the current local mechanism path has reached diminishing returns and requires a broader redesign question.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 14:11 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:15 (Pacific/Honolulu)
- Decision: `STOP` the fixed post-`RZ` mixing preset branch as an active improvement track. Keep `mix_v0` as baseline and move to a broader local redesign question.
