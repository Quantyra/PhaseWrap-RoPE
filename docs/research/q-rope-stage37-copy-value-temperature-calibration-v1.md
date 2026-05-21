# PhaseWrap-RoPE Stage 37 Copy-Value Temperature Calibration v1

Date: `2026-05-20`

Status: `completed`

## Purpose

Stage 37 applies validation-selected post-hoc temperature calibration to the Stage 36 copy-value bridge. The model shape and copy-style value output are unchanged: the benchmark trains learned attention on Stage 14 key-value rows, then selects a scalar attention temperature on validation loss before evaluating held-out value-token retrieval.

This tests whether the remaining Stage 36 probability-mass gap is mainly a scalar sharpness issue.

## Reviewer Command

```bash
python scripts/run_stage37_copy_value_temperature_calibration.py
```

This writes:

- `logs/automated_stage_gates/stage37_copy_value_temperature_calibration/manifest.json`
- `logs/automated_stage_gates/stage37_copy_value_temperature_calibration/results.json`
- `logs/automated_stage_gates/stage37_copy_value_temperature_calibration/summary.csv`
- `logs/automated_stage_gates/stage37_copy_value_temperature_calibration/per_run_results.csv`
- `logs/automated_stage_gates/stage37_copy_value_temperature_calibration/task_summary.csv`
- `logs/automated_stage_gates/stage37_copy_value_temperature_calibration/weak_runs.json`

## Result

Temperature calibration sharply improves target probability and calibration for the solved copy-value methods:

| Method | Top-1 | MRR | Mean target value probability | ECE | Delta target value probability | Selected temperature |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `rope_relative` | 1.000000 | 1.000000 | 0.998545 | 0.001455 | 0.340426 | 0.250000 |
| `phasewrap_multiscale_adapter` | 1.000000 | 1.000000 | 0.920368 | 0.081020 | 0.406105 | 0.250000 |
| `phasewrap_distance_adapter` | 1.000000 | 1.000000 | 0.907215 | 0.093572 | 0.457952 | 0.250000 |
| `sinusoidal` | 0.816667 | 0.905556 | 0.777826 | 0.073812 | 0.285280 | 0.330000 |
| `no_position` | 0.096667 | 0.216891 | 0.042769 | 0.041802 | 0.000101 | 0.250000 |
| `alibi` | 0.090000 | 0.215422 | 0.043046 | 0.034174 | 0.000307 | 0.250000 |

## Interpretation

Stage 37 shows that a large part of the Stage 36 probability-mass weakness is scalar sharpness: the PhaseWrap-derived copy-value bridges keep perfect held-out top-1/MRR and move from roughly `0.45-0.51` target value probability to roughly `0.91-0.92`.

The result does not close the RoPE-facing gap. `rope_relative` also sharpens and reaches mean target value probability `0.998545` with ECE `0.001455`, so RoPE-like scoring remains the strongest calibrated copy-value bridge in this packet.

## Claim Boundary

Supported:

- deterministic post-hoc calibration evidence for the Stage 36 copy-value bridge;
- evidence that scalar temperature can substantially improve PhaseWrap-derived target probability under hardened value output;
- evidence that RoPE-like scoring still keeps the best calibrated probability mass;
- matched data splits, feature width, hidden width, model seeds, confidence intervals, and weak-run reporting.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- a claim that PhaseWrap-RoPE is a validated RoPE replacement.
