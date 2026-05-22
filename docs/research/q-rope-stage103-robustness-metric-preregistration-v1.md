# PhaseWrap-RoPE Stage 103 Robustness Metric Preregistration v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 103 predeclares how future calibrated noisy-hardware packet counts will be reduced into robustness and auditability metrics.

Stage 99 froze matched product-state packets. Stage 100 froze matched CX/parity packets. Stage 101 blocks interpretation until known-state calibration passes. Stage 102 provides calibration execution templates. Stage 104 validates the complete fixed-width comparator handoff. Stage 103 now freezes the metric rules before hardware result inspection.

## Reviewer Command

```bash
python scripts/run_stage103_robustness_metric_preregistration.py
```

This writes:

- `logs/automated_stage_gates/stage103_robustness_metric_preregistration/manifest.json`
- `logs/automated_stage_gates/stage103_robustness_metric_preregistration/results.json`
- `logs/automated_stage_gates/stage103_robustness_metric_preregistration/summary.csv`

## Result

Current decision:

`ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED`

This is expected. The metric plan is frozen, but Stage 101 calibration has not passed and no calibrated Stage 99/100 packet counts are present.

## Metric Rules

Primary robustness metric:

- mean absolute score error between calibrated measured score and ideal packet score.

Secondary metrics:

- root mean squared score error;
- Spearman rank correlation between ideal and measured row scores;
- top-1 row agreement;
- row coverage fraction;
- shot-count consistency.

Score reconstruction:

- Product-state packets: `0.5 + 0.25 * (E[Z0] + E[Z1])`
- CX/parity packets: `0.5 + 0.25 * (E[Z0 after CX] + E[Z0 Z1 after CX])`

Counts must be canonical `q0q1` decoded after Stage 101 calibration and must come from Stage 113-assembled packet evidence. Interpretation also requires Stage 104 to report complete provider/lane/template comparator groups.

## Advantage Rule

PhaseWrap may be described as lower-error on a lane only if its mean absolute score error is lower than each named comparator family on the same provider, source lane, and circuit template after Stage 101 calibration passes.

The named comparators are:

- `rope_like`
- `sinusoidal_like`
- `alibi_like`
- `no_position_control`

## Claim Boundary

Supported:

- predeclared robustness and auditability metrics for future calibrated Stage 99 and Stage 100 packet executions;
- fixed score reconstruction formulas for product-state and CX/parity packet families;
- a hard block against non-Stage-113 packet evidence;
- a hard block unless Stage 104 exposes complete fixed-width provider/lane/template comparator groups;
- a hard separation between metric preregistration and any future hardware advantage claim.

Excluded:

- a noisy-hardware robustness result without calibrated packet counts;
- a PhaseWrap advantage claim before Stage 101 passes and all matched packet counts are present;
- production transformer superiority;
- broad quantum advantage.
