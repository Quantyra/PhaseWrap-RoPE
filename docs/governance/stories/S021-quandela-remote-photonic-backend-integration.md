# Story template

## Story ID and title
S021 - Quandela remote photonic backend integration

## User value
As a research lead, I want an actual photonic cloud execution path integrated into the Q-RoPE runner, so the project has real remote-backend evidence instead of simulator-only claims.

## Acceptance criteria
- `qrope.run` supports a Quandela remote backend using repo-managed credentials.
- A real remote artifact is generated and stored under `logs/ablation_runs/`.
- Reporting distinguishes canonical phase-1 matrix rows from supplemental backend-extension rows.
- Runbook and evidence log are updated.

## Outputs
- `src/qrope/qphotonic.py`
- `src/qrope/env_utils.py`
- `docs/research/q-rope-quandela-remote-backend-v1.md`
- `logs/ablation_runs/v3-yelp-quandela-s42/metrics.json`

## Evidence and references
- `docs/research/q-rope-ablation-runbook-v1.md`
- `docs/evidence/E001-evidence-log.md`

## Out of scope
- Matched multi-seed Quandela matrix execution
- Hardware-device claims

## Dependencies
- S018
- S020

## Risks
- Cloud latency and provider payload constraints may force reduced evaluation slices.

## Unit tests (development stories only)
- `python -m pytest tests/test_run_real_mode.py tests/test_qphotonic.py tests/test_stats_report.py tests/test_report_counts.py tests/test_config_merge.py`

## Cycle time
- Start: 2026-03-06 02:10 (Pacific/Honolulu)
- End: 2026-03-06 02:34 (Pacific/Honolulu)
- Total: 00:24

## Notes
- Completed with authenticated `sim:slos` execution and a stored remote artifact.
- Reporting now preserves the canonical phase-1 matrix and isolates supplemental backend runs.
- The provider accepted a minimal beam-splitter path; richer circuit compositions were rejected by the active remote endpoint.
