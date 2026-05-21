# PhaseWrap-RoPE Stage 38 Hardened Decoder Value Bridge v1

Date: `2026-05-20`

Status: `completed`

## Purpose

Stage 38 returns to the learned decoder-style value path after the Stage 36/37 copy-value diagnostics. It keeps learned positional attention plus learned value embeddings/output projection, but hardens capacity and training: hidden width `16`, value embedding width `64`, `33,378` learned parameters, and `360` full-batch Adam epochs.

This tests whether the Stage 34 weakness was mostly a small-capacity/training issue once the copy-value shortcut is removed.

## Reviewer Command

```bash
python scripts/run_stage38_hardened_decoder_value_bridge.py
```

This writes:

- `logs/automated_stage_gates/stage38_hardened_decoder_value_bridge/manifest.json`
- `logs/automated_stage_gates/stage38_hardened_decoder_value_bridge/results.json`
- `logs/automated_stage_gates/stage38_hardened_decoder_value_bridge/summary.csv`
- `logs/automated_stage_gates/stage38_hardened_decoder_value_bridge/train_summary.csv`
- `logs/automated_stage_gates/stage38_hardened_decoder_value_bridge/validation_summary.csv`
- `logs/automated_stage_gates/stage38_hardened_decoder_value_bridge/per_run_results.csv`
- `logs/automated_stage_gates/stage38_hardened_decoder_value_bridge/task_summary.csv`
- `logs/automated_stage_gates/stage38_hardened_decoder_value_bridge/weak_runs.json`

## Result

All methods fit the training rows nearly perfectly, but held-out length generalization remains weak and favors RoPE-like scoring:

| Method | Test top-1 | Test MRR | Test target value probability | Train top-1 | Train target value probability |
| --- | ---: | ---: | ---: | ---: | ---: |
| `rope_relative` | 0.370000 | 0.419859 | 0.350489 | 1.000000 | 0.997951 |
| `phasewrap_multiscale_adapter` | 0.306667 | 0.358125 | 0.213638 | 1.000000 | 0.998301 |
| `sinusoidal` | 0.276667 | 0.346272 | 0.173487 | 1.000000 | 0.997989 |
| `phasewrap_distance_adapter` | 0.270000 | 0.333913 | 0.181079 | 1.000000 | 0.998144 |
| `no_position` | 0.023333 | 0.065264 | 0.010029 | 1.000000 | 0.997190 |
| `alibi` | 0.020000 | 0.051514 | 0.007595 | 1.000000 | 0.997275 |

## Interpretation

Stage 38 does not support the idea that Stage 34 was merely too small or undertrained. The hardened model can memorize the train rows, but generalization to held-out length `1024` remains limited.

The ordering is still RoPE-favorable under the learned value-output path: `rope_relative` leads test top-1, MRR, and target value probability. The PhaseWrap-derived adapters remain better than no-position and ALiBI in this packet, but they do not match the RoPE-like result once learned value output is required.

Combined with Stage 36/37, the picture is now sharper: PhaseWrap-derived attention features can recover ranking when value output copies candidate values directly, and scalar calibration can improve copy-value probability mass. However, the full learned value-output bridge still creates a generalization bottleneck where RoPE-like scoring remains strongest.

## Claim Boundary

Supported:

- deterministic hardened decoder-style value-bridge evidence on non-phase-cued key-value retrieval rows;
- evidence that capacity/training hardening solves train fit but not held-out length generalization;
- evidence that RoPE-like scoring remains strongest under learned value-output decoding;
- matched data splits, feature width, hidden width, value embedding width, model seeds, confidence intervals, and weak-run reporting.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- a claim that PhaseWrap-RoPE is a validated RoPE replacement.
