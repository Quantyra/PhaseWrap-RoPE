# Story template

## Story ID and title
S022 - IBM Runtime remote backend integration

## User value
As a research lead, I want IBM Runtime integrated as a secondary remote comparator, so Q-RoPE can be tested on a non-photonic cloud backend without blocking the photonic-primary strategy.

## Acceptance criteria
- `qrope.run` supports an IBM Runtime backend using token-only initialization.
- One minimal remote artifact is generated through the repo pipeline.
- Documentation states this is a secondary comparator track.

## Outputs
- `src/qrope/run.py`
- `docs/research/`
- `logs/ablation_runs/`

## Evidence and references
- `scripts/ibm_runtime_check.py`
- `docs/research/q-rope-open-source-and-cloud-strategy-v1.md`

## Out of scope
- Large IBM ablation matrix
- Hardware-priority claims over photonic execution

## Dependencies
- S021

## Risks
- Platform quotas, queue times, and backend availability may vary by date and account tier.

## Unit tests (development stories only)
- Update existing local unit coverage as needed.

## Cycle time
- Start: 2026-03-06 02:35 (Pacific/Honolulu)
- End: 2026-03-06 05:03 (Pacific/Honolulu)
- Total: 02:28

## Notes
- Completed with a real IBM Runtime artifact at `logs/ablation_runs/v3-yelp-ibm-s42/metrics.json`.
- Implementation uses token-only initialization and batched `SamplerV2` jobs.
- IBM remains the secondary comparator track; photonic execution remains primary.
