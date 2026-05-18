# Story template

## Story ID and title
S011 - Train/inference integration for real metrics

## User value
As a research lead, I want the ablation pipeline wired to real model training and inference, so reports reflect empirical results instead of dry-run placeholders.

## Acceptance criteria
- `qrope.run` executes training/inference path for at least one dataset.
- `metrics.json` includes non-placeholder model metrics and measured wall time.
- Dry-run and real-run modes are explicitly distinguished in output.

## Outputs
- Updated `src/qrope/run.py`
- Real-run artifact sample under `logs/ablation_runs/`

## Evidence and references
- `docs/research/q-rope-ablation-runbook-v1.md`
- `configs/ablation/`

## Out of scope
- Full multi-backend hardware comparison.

## Dependencies
- S010

## Risks
- Architecture integration complexity may require incremental rollout by dataset.

## Unit tests (development stories only)
- Add/extend tests for run-mode branching and required metrics schema.

## Cycle time
- Start: 2026-03-05 08:33 (Pacific/Honolulu)
- End: 2026-03-05 08:40 (Pacific/Honolulu)
- Total: 00:07

## Notes
- This story unlocks first publishable empirical evidence.
- Completion: `qrope.run` now supports explicit dry vs real modes, produced non-placeholder metrics in real mode, and aggregation schema tracks `run_mode` and `data_mode`.
- Caveat: initial real-run evidence currently uses synthetic fallback data because no local dataset files are present.
