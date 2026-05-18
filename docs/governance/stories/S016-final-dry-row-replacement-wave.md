# Story template

## Story ID and title
S016 - Final dry-row replacement wave

## User value
As a research lead, I want to eliminate remaining dry rows, so the ablation matrix is fully real-mode for current local datasets.

## Acceptance criteria
- Replace all remaining dry rows in `summary_v1.csv`.
- Regenerated report shows `dry=0`.
- Validate run-mode count logic with test pass.

## Outputs
- updated `logs/ablation_runs/summary/summary_v1.csv`
- updated `logs/ablation_runs/summary/report_v1.md`

## Evidence and references
- `stories/S015-amazon-real-data-ingestion-and-replacement-wave-2.md`
- `docs/research/q-rope-ablation-runbook-v1.md`

## Out of scope
- Formal publication tables and confidence intervals.

## Dependencies
- S015

## Risks
- Real-mode metrics can still be unstable due to limited handcrafted dataset size.

## Unit tests (development stories only)
- Re-run `test_report_counts.py`.

## Cycle time
- Start: 2026-03-05 09:21 (Pacific/Honolulu)
- End: 2026-03-05 09:30 (Pacific/Honolulu)
- Total: 00:09

## Notes
- Expected dry rows to replace: 12 (seed `777` across three datasets and four variants).
- Completion: replaced all remaining 12 dry rows with real-mode runs.
- Final run-mode counts: `real=42`, `dry=0`.
