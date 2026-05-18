# Story template

## Story ID and title
S013 - Real-data matrix expansion

## User value
As a research lead, I want real-data runs across additional datasets/variants, so ablation summaries are not dominated by dry-run placeholders.

## Acceptance criteria
- Add at least one more local dataset file (`imdb` or `amazon`).
- Execute at least one real-data run for each variant (`V0-V3`) on one real dataset.
- Report separates dry-run and real-run counts clearly.

## Outputs
- `data/imdb.jsonl` or `data/amazon.jsonl`
- updated `logs/ablation_runs/summary/summary_v1.csv`
- updated `logs/ablation_runs/summary/report_v1.md`

## Evidence and references
- `stories/S012-real-data-ingestion-and-slice-rerun.md`
- `docs/research/q-rope-ablation-runbook-v1.md`

## Out of scope
- Final statistical significance package.

## Dependencies
- S012

## Risks
- Limited local data size can produce unstable metric variance.

## Unit tests (development stories only)
- Add a summary check that reports real-run counts by variant.

## Cycle time
- Start: 2026-03-05 08:53 (Pacific/Honolulu)
- End: 2026-03-05 09:02 (Pacific/Honolulu)
- Total: 00:09

## Notes
- This story transitions from proof-of-path to minimally balanced real-data ablations.
- Completion: added `data/imdb.jsonl`, executed real-mode coverage for `V0-V3` on local `yelp` slice, and updated report with explicit run-mode counts (`real=6`, `dry=36`).
