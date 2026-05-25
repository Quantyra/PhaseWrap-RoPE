# Stage 219 RoPE-Substitution Gate v1

Date: `2026-05-23`

Status: `complete`

Decision: `BOUNDED_PHASEWRAP_ROPE_SUBSTITUTION_SUPPORTED_WITH_MEASURED_CALIBRATION_DEGRADATION`

## Question

Can PhaseWrap be used in place of RoPE in a bounded non-phase-cued retrieval-bridge benchmark, even if RoPE remains better on probability and calibration?

## Evidence Inputs

Stage 219 reads the existing raw benchmark outputs:

- `logs/automated_stage_gates/stage30_matched_retrieval_bridge/results.json`
- `logs/automated_stage_gates/stage32_full_context_feature_bridge/results.json`

The primary gate is Stage 30. Stage 32 is a corroborating full-context feature-bridge gate.

## Adequacy Criteria

The gate requires at least five model initialization seeds, matched parameter count and run count, PhaseWrap top-1 at least `0.90`, PhaseWrap MRR at least `0.95`, top-1 degradation versus RoPE no more than `0.10`, MRR degradation versus RoPE no more than `0.05`, lift over `no_position` and sinusoidal controls, and explicit recording of RoPE's probability/calibration advantage.

## Result

Primary Stage 30 gate:

- PhaseWrap method: `phasewrap_distance_adapter`
- RoPE method: `rope_relative`
- PhaseWrap top-1: `1.000000`
- PhaseWrap MRR: `1.000000`
- top-1 degradation versus RoPE: `0.000000`
- MRR degradation versus RoPE: `0.000000`
- mean target-probability degradation versus RoPE: `0.179917`
- expected-calibration-error degradation versus RoPE: `0.185967`

Secondary Stage 32 corroboration:

- PhaseWrap method: `phasewrap_multiscale_adapter`
- RoPE method: `rope_relative`
- PhaseWrap top-1: `1.000000`
- PhaseWrap MRR: `1.000000`
- top-1 degradation versus RoPE: `0.000000`
- MRR degradation versus RoPE: `0.000000`
- mean target-probability degradation versus RoPE: `0.232716`
- expected-calibration-error degradation versus RoPE: `0.238330`

## Supported Claim

PhaseWrap-derived adapters are viable RoPE substitutes in these bounded retrieval-bridge benchmarks: they preserve held-out retrieval top-1/MRR within the predeclared margin while showing measured degradation versus RoPE on probability, calibration, and loss.

## Boundary

This does not establish general RoPE replacement, production transformer superiority, language-model-scale validation, or quantum advantage.

Run:

```bash
python scripts/run_stage219_rope_substitution_gate.py
```
