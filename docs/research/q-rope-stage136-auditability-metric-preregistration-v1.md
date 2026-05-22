# QRoPE Stage 136 - Auditability Metric Preregistration

## Objective
Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, under fixed circuit width.

## Result
Stage 136 preregisters the auditability branch of the hardware goal. It validates that the Stage 99 product-state and Stage 100 CX/parity packets carry the row-level trace fields needed to evaluate auditability after hardware counts are available, and that each provider/lane/template group preserves the same fixed-width comparator surface used by the robustness branch.

Current decision: `AUDITABILITY_METRIC_CONTRACT_READY_HARDWARE_COUNTS_REQUIRED`.

## Preregistered Metrics
- Static trace coverage: every row must preserve source-row hash, source deltas, two ideal score components, circuit parameters, ideal score prediction, and row hash.
- Hardware auditability metric: after Stage 101 calibration, reconstruct `component_a` and `component_b` from the same calibrated observables used by Stage 103, then compute component reconstruction mean absolute error against the frozen packet components.
- Advantage rule: PhaseWrap may be described as having an auditability advantage only for a provider, source lane, and circuit template where trace coverage is complete for every matched family and PhaseWrap's component reconstruction MAE is lower than every named positional comparator family in the same calibrated hardware evidence window.
- Fixed-width binding: each provider/lane/template group must contain the full PhaseWrap, RoPE-like, sinusoidal-like, ALIBI-like, and no-position/control set with matching row-set hashes, row counts, shot counts, two measured qubits, computational-basis readout, and an allowed product-state or CX/parity circuit template.

The no-position/control family remains a control for auditability wording; it is not treated as a positional method PhaseWrap must beat for the auditability-specific claim.

## Claim Boundary
Supported:

- auditability metrics are now measurable and preregistered for the matched fixed-width packet families
- all current Stage 99/100 packet rows expose the static trace fields needed for later component reconstruction checks
- the auditability branch remains bound to the same fixed-width, same-row, same-shot-budget, same-calibration evidence surface as robustness

Excluded:

- hardware job submission
- provider credentials or secret values
- new provider result records
- a current auditability advantage claim
- a robustness advantage claim

## Evidence
- `logs/automated_stage_gates/stage136_auditability_metric_preregistration/manifest.json`
- `logs/automated_stage_gates/stage136_auditability_metric_preregistration/results.json`
- `logs/automated_stage_gates/stage136_auditability_metric_preregistration/summary.csv`
