# PhaseWrap-RoPE Stage 36 Copy-Value Bridge v1

Date: `2026-05-20`

Status: `completed`

## Purpose

Stage 36 hardens the Stage 34/35 value-output path by replacing the learned value-token classifier with copy-style value output. The model still learns positional attention from the same Stage 14 key-value rows, but the output distribution is formed by copying attention mass onto candidate value tokens.

This tests whether the learned attention mechanism can select the right candidate when the value-output bottleneck is no longer the limiting classifier.

## Reviewer Command

```bash
python scripts/run_stage36_copy_value_bridge.py
```

This writes:

- `logs/automated_stage_gates/stage36_copy_value_bridge/manifest.json`
- `logs/automated_stage_gates/stage36_copy_value_bridge/results.json`
- `logs/automated_stage_gates/stage36_copy_value_bridge/summary.csv`
- `logs/automated_stage_gates/stage36_copy_value_bridge/per_run_results.csv`
- `logs/automated_stage_gates/stage36_copy_value_bridge/task_summary.csv`
- `logs/automated_stage_gates/stage36_copy_value_bridge/weak_runs.json`

## Result

With copy-style value output, PhaseWrap-derived adapters recover perfect held-out ranking:

| Method | Top-1 | MRR | Mean target value probability | Mean target attention probability |
| --- | ---: | ---: | ---: | ---: |
| `rope_relative` | 1.000000 | 1.000000 | 0.659427 | 0.657819 |
| `phasewrap_multiscale_adapter` | 1.000000 | 1.000000 | 0.510753 | 0.508839 |
| `phasewrap_distance_adapter` | 1.000000 | 1.000000 | 0.447922 | 0.444551 |
| `sinusoidal` | 0.810000 | 0.902778 | 0.493643 | 0.488818 |
| `no_position` | 0.106667 | 0.219510 | 0.042662 | 0.037903 |
| `alibi` | 0.086666 | 0.213189 | 0.042749 | 0.037977 |

## Interpretation

Stage 36 materially changes the interpretation of Stage 34 and Stage 35. Once value output is hardened by copying candidate values, both `phasewrap_distance_adapter` and `phasewrap_multiscale_adapter` recover top-1 `1.000000` and MRR `1.000000` on the held-out rows.

This suggests the Stage 34 weakness was substantially caused by the learned value-token output path, not by an inability of the PhaseWrap-derived attention features to select the correct candidate under this bridge. The remaining caveat is probability mass: `rope_relative` still gives higher target value probability than the PhaseWrap-derived adapters.

## Claim Boundary

Supported:

- deterministic copy-value bridge evidence on non-phase-cued key-value retrieval rows;
- evidence that current PhaseWrap-derived adapters can recover held-out top-1/MRR when value-output coupling is hardened;
- evidence that RoPE-like scoring still has stronger target probability mass on this packet;
- matched data splits, feature width, hidden width, model seeds, confidence intervals, and weak-run reporting.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- a claim that PhaseWrap-RoPE is a validated RoPE replacement.
