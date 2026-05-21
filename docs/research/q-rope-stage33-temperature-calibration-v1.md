# PhaseWrap-RoPE Stage 33 Temperature Calibration Audit v1

Date: `2026-05-20`

Status: `completed`

## Purpose

Stage 33 audits whether the Stage 32 target-probability and calibration gap is mainly a scalar temperature issue. It reuses the Stage 32 one-hidden-layer full-context feature bridge on Stage 12 non-phase-cued retrieval rows, selects one post-hoc temperature from a fixed grid on validation loss, and evaluates the held-out test rows.

Targets are selected by explicit retrieval rules, not by maximizing the PhaseWrap score.

## Reviewer Command

```bash
python scripts/run_stage33_temperature_calibration.py
```

This writes:

- `logs/automated_stage_gates/stage33_temperature_calibration/manifest.json`
- `logs/automated_stage_gates/stage33_temperature_calibration/results.json`
- `logs/automated_stage_gates/stage33_temperature_calibration/summary.csv`
- `logs/automated_stage_gates/stage33_temperature_calibration/per_run_results.csv`
- `logs/automated_stage_gates/stage33_temperature_calibration/weak_runs.json`

## Design

Every method uses:

- the same Stage 12 train/validation/test split;
- five deterministic model initialization seeds;
- the same Stage 32 nonlinear full-context feature bridge;
- validation-selected post-hoc temperature over a fixed grid;
- test-set reporting for calibrated metrics, uncalibrated target probability/ECE, and calibration deltas;
- confidence intervals over model initialization seeds;
- explicit weak-run reporting.

## Result

On the default artifact, `rope_relative`, `phasewrap_distance_adapter`, and `phasewrap_multiscale_adapter` all retain mean top-1 `1.000000` and mean MRR `1.000000` after temperature calibration.

Temperature scaling improves target probability and expected calibration error for all solved methods, but it does not remove the RoPE-like probability/calibration lead:

| Method | Top-1 | MRR | Mean target probability | ECE | Delta target probability | Delta ECE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `rope_relative` | 1.000000 | 1.000000 | 0.993605 | 0.006395 | 0.280579 | -0.284761 |
| `phasewrap_multiscale_adapter` | 1.000000 | 1.000000 | 0.960102 | 0.041080 | 0.479792 | -0.488406 |
| `phasewrap_distance_adapter` | 1.000000 | 1.000000 | 0.917118 | 0.084114 | 0.488044 | -0.497286 |
| `sinusoidal` | 0.786667 | 0.888334 | 0.748011 | 0.086060 | 0.319681 | -0.286457 |

The selected temperature is `0.25` for all five seeds of every method in this artifact.

## Interpretation

Stage 33 shows that the Stage 32 calibration gap is partly a post-hoc sharpness issue: all solved methods become much more confident on the correct held-out positions after validation-selected temperature scaling.

The result also preserves the bounded ordering. PhaseWrap multiscale and distance adapters remain competitive by argmax retrieval, but `rope_relative` still has the strongest calibrated target probability and ECE on this compact full-context bridge.

## Claim Boundary

Supported:

- deterministic post-hoc temperature calibration audit of the Stage 32 full-context bridge;
- evidence that PhaseWrap-derived adapters keep perfect argmax retrieval after calibration on this packet;
- evidence that RoPE-like scoring still leads calibrated probability/ECE on this packet;
- confidence intervals over initialization seeds and explicit weak-run reporting.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- a claim that PhaseWrap-RoPE is a validated RoPE replacement.
