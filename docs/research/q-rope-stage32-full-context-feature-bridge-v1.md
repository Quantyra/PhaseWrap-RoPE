# PhaseWrap-RoPE Stage 32 Full-Context Feature-Bridge Benchmark v1

Date: `2026-05-20`

Status: `completed`

## Purpose

Stage 32 follows the Stage 31 full-prefix retrieval-attention failure by testing a richer nonlinear feature bridge while still making every prefix position compete. It reuses the Stage 12 non-phase-cued passkey, multi-needle, and aggregation rows.

Targets are selected by explicit retrieval rules, not by maximizing the PhaseWrap score.

## Reviewer Command

```bash
python scripts/run_stage32_full_context_feature_bridge.py
```

This writes:

- `logs/automated_stage_gates/stage32_full_context_feature_bridge/manifest.json`
- `logs/automated_stage_gates/stage32_full_context_feature_bridge/results.json`
- `logs/automated_stage_gates/stage32_full_context_feature_bridge/summary.csv`
- `logs/automated_stage_gates/stage32_full_context_feature_bridge/per_run_results.csv`
- `logs/automated_stage_gates/stage32_full_context_feature_bridge/task_summary.csv`
- `logs/automated_stage_gates/stage32_full_context_feature_bridge/weak_runs.json`

## Design

Every method uses:

- the same Stage 12 train/validation/test split;
- five deterministic model initialization seeds;
- a learned full-prefix attention distribution over all positions before the query;
- feature width `12`;
- hidden width `10`;
- learned parameter count `141`;
- the same optimizer, epochs, learning rate, and L2 penalty;
- confidence intervals over model initialization seeds;
- explicit weak-run reporting.

## Result

On the default artifact, `rope_relative`, `phasewrap_distance_adapter`, and `phasewrap_multiscale_adapter` all reach mean top-1 `1.000000` and mean MRR `1.000000`.

`rope_relative` remains stronger on probability and calibration metrics:

- `rope_relative` mean target probability: `0.713026`
- `phasewrap_multiscale_adapter` mean target probability: `0.480310`
- `phasewrap_distance_adapter` mean target probability: `0.429075`
- `rope_relative` expected calibration error: `0.291156`
- `phasewrap_multiscale_adapter` expected calibration error: `0.529486`
- `phasewrap_distance_adapter` expected calibration error: `0.581401`

## Interpretation

Stage 32 shows that the Stage 31 full-prefix failure was not inevitable for PhaseWrap-derived features: a nonlinear full-context feature bridge recovers argmax retrieval for PhaseWrap distance and multiscale adapters.

The result remains bounded. It is still a compact feature bridge, not a full decoder-only language-model benchmark. It does not establish that PhaseWrap-RoPE replaces RoPE because RoPE-like scoring keeps stronger target probability and calibration on the same held-out rows.

## Claim Boundary

Supported:

- deterministic multi-initialization nonlinear full-context retrieval bridge on non-phase-cued Stage 12 rows;
- direct follow-up to the Stage 31 simple-attention failure using richer PhaseWrap-derived features;
- confidence intervals over initialization seeds and explicit weak-run reporting.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- a claim that PhaseWrap-RoPE is a validated RoPE replacement.
