# QRoPE Stage 137 - Auditability Metric Evaluator

## Objective
Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, under fixed circuit width.

## Result
Stage 137 implements the hardware-count-dependent auditability evaluator preregistered in Stage 136.

Current decision: `AUDITABILITY_METRICS_BLOCKED_HARDWARE_COUNTS_REQUIRED`.

The evaluator reads the Stage 107 independent-window plan, requires Stage 136 to expose complete fixed-width provider/lane/template comparator groups, requires each window's Stage 101 calibration result to pass, requires packet execution files to carry Stage 113 assembly status and live-submit provenance, then reconstructs `component_a` and `component_b` from the same packet execution counts used by Stage 103:

- product-state template: `component_a = E[Z0]`, `component_b = E[Z1]`
- CX/parity template: `component_a = E[Z0]`, `component_b = E[Z0 Z1]`

It computes component reconstruction mean absolute error per packet family and applies the Stage 136 auditability advantage rule against the named positional comparators. The no-position/control packet must be present as a control-family member of the fixed-width comparison group, but it is not treated as a positional comparator PhaseWrap must beat for auditability-specific wording.

## Claim Boundary
Supported:

- deterministic component-reconstruction auditability evaluator
- Stage 136 fixed-width provider/lane/template group readiness checked before evaluation
- same-window binding to Stage 107 packet counts and Stage 101 calibration results
- auditability interpretation requires Stage 113-assembled packet evidence
- auditability comparison groups require PhaseWrap, every named positional comparator, and no-position/control evidence
- blocked output while real provider packet counts are missing

Excluded:

- hardware job submission
- provider credentials or secret values
- new provider result records
- a current auditability advantage claim unless this gate is ready and the advantage rule passes
- a robustness advantage claim

## Evidence
- `logs/automated_stage_gates/stage137_auditability_metric_evaluator/manifest.json`
- `logs/automated_stage_gates/stage137_auditability_metric_evaluator/results.json`
- `logs/automated_stage_gates/stage137_auditability_metric_evaluator/summary.csv`
