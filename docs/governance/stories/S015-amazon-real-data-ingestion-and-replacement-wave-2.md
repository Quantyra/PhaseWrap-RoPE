# Story template

## Story ID and title
S015 - Amazon real-data ingestion and replacement wave 2

## User value
As a research lead, I want Amazon local data integrated and used for real-mode replacement, so all three core datasets have empirical runs.

## Acceptance criteria
- Add `data/amazon.jsonl` local dataset slice.
- Replace at least 8 dry rows for Amazon with real runs across variants.
- Update report run-mode counts and verify trend toward real-run majority.

## Outputs
- `data/amazon.jsonl`
- updated `logs/ablation_runs/summary/summary_v1.csv`
- updated `logs/ablation_runs/summary/report_v1.md`

## Evidence and references
- `stories/S014-real-mode-replacement-wave-1.md`
- `docs/research/q-rope-ablation-runbook-v1.md`

## Out of scope
- Full significance analysis and manuscript-ready charts.

## Dependencies
- S014

## Risks
- Small handcrafted local dataset may underrepresent true Amazon distribution.

## Unit tests (development stories only)
- Re-run report count test and dataset loader test after ingestion.

## Cycle time
- Start: 2026-03-05 09:13 (Pacific/Honolulu)
- End: 2026-03-05 09:20 (Pacific/Honolulu)
- Total: 00:07

## Notes
- This wave targets three-dataset real-mode coverage baseline.
- Completion: added `data/amazon.jsonl` and replaced 8 Amazon dry rows with real runs (`V0-V3`, seeds `42` and `123`).
- Post-wave run-mode counts: `real=30`, `dry=12`.
