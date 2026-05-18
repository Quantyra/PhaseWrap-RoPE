# Story template

## Story ID and title
S014 - Real-mode replacement wave 1

## User value
As a research lead, I want the first large replacement wave from dry to real runs, so the ablation summary becomes empirically meaningful.

## Acceptance criteria
- Replace at least 12 dry rows with real-mode runs.
- Cover at least two datasets in real mode.
- Keep run-mode count table updated and validated.

## Outputs
- updated `logs/ablation_runs/summary/summary_v1.csv`
- updated `logs/ablation_runs/summary/report_v1.md`

## Evidence and references
- `stories/S013-real-data-matrix-expansion.md`
- `docs/research/q-rope-ablation-runbook-v1.md`

## Out of scope
- Final statistical manuscript tables.

## Dependencies
- S013

## Risks
- Small local dataset slices may skew early metric distributions.

## Unit tests (development stories only)
- Validate report counts after replacement wave.

## Cycle time
- Start: 2026-03-05 09:03 (Pacific/Honolulu)
- End: 2026-03-05 09:12 (Pacific/Honolulu)
- Total: 00:09

## Notes
- Priority order for replacement: V3 -> V2 -> V1 -> V0.
- Completion: replaced 16 dry rows with real-mode runs (`V0-V3` across `yelp` and `imdb`, seeds `42` and `123`) by overwriting original run IDs.
- Run-mode counts after wave: `real=22`, `dry=20`.
