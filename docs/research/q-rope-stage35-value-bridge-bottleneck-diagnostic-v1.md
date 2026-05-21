# PhaseWrap-RoPE Stage 35 Value-Bridge Bottleneck Diagnostic v1

Date: `2026-05-20`

Status: `completed`

## Purpose

Stage 35 diagnoses the Stage 34 compact decoder-style value bridge by removing learned positional selection. It uses the same Stage 14 key-value rows, but supplies teacher-forced target-position attention and trains only the value embeddings plus output projection.

This answers a narrow question: if the position is already selected correctly, does the value-output path generalize well enough on the held-out length-1024 rows?

## Reviewer Command

```bash
python scripts/run_stage35_value_bridge_bottleneck_diagnostic.py
```

This writes:

- `logs/automated_stage_gates/stage35_value_bridge_bottleneck_diagnostic/manifest.json`
- `logs/automated_stage_gates/stage35_value_bridge_bottleneck_diagnostic/results.json`
- `logs/automated_stage_gates/stage35_value_bridge_bottleneck_diagnostic/summary.csv`
- `logs/automated_stage_gates/stage35_value_bridge_bottleneck_diagnostic/per_run_results.csv`
- `logs/automated_stage_gates/stage35_value_bridge_bottleneck_diagnostic/task_summary.csv`
- `logs/automated_stage_gates/stage35_value_bridge_bottleneck_diagnostic/weak_runs.json`

## Result

Teacher-forced target attention improves the value path over Stage 34 but does not solve it:

| Label | Top-1 | MRR | Mean target value probability | ECE |
| --- | ---: | ---: | ---: | ---: |
| `alibi` | 0.530000 | 0.550027 | 0.490825 | 0.061432 |
| `no_position` | 0.526667 | 0.547837 | 0.490637 | 0.059868 |
| `rope_relative` | 0.526667 | 0.546979 | 0.494107 | 0.054225 |
| `phasewrap_distance_adapter` | 0.520000 | 0.542044 | 0.490226 | 0.052834 |
| `sinusoidal` | 0.506667 | 0.538282 | 0.490351 | 0.059273 |
| `phasewrap_multiscale_adapter` | 0.500000 | 0.532762 | 0.488968 | 0.049903 |

The diagnostic verdict is:

```text
value_output_partly_viable_attention_selection_still_primary
```

## Interpretation

The Stage 34 gap is not explained by PhaseWrap position features alone. When target attention is supplied, all method labels converge near the same value-output performance, around top-1 `0.50-0.53` and target value probability around `0.49`.

This means:

- learned positional selection remains a major Stage 34 bottleneck;
- value-output capacity/generalization is also not fully solved;
- the next mechanism work should avoid scaling the current adapter unchanged and should instead harden both attention selection and value-output coupling.

## Claim Boundary

Supported:

- deterministic teacher-forced diagnostic separating value-output behavior from learned positional selection;
- evidence that the value-output path is partly viable but not solved;
- evidence that Stage 34 still has a major learned-attention/mechanism bottleneck;
- matched data splits, optimizer, value-output dimensions, confidence intervals, and weak-run reporting.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- a claim that PhaseWrap-RoPE is a validated RoPE replacement.
