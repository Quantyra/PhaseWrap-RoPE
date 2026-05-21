# PhaseWrap-RoPE Stage 41 Pointer/Copy Sequence v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 41 tests whether the Stage 39/40 all-prefix sequence decoder failure is primarily a learned value-output/generalization bottleneck. It keeps the Stage 40 length curriculum, full-prefix token competition, feature bridge, optimizer, and five model initialization seeds, but replaces the learned value-token classifier with a deterministic pointer/copy head.

The value output is computed as copied attention mass over observed prefix token IDs. This is a diagnostic of attention selection plus copy-style value coupling, not a production decoder-only transformer benchmark.

## Reviewer Command

```bash
python scripts/run_stage41_pointer_copy_sequence.py
```

This writes:

- `logs/automated_stage_gates/stage41_pointer_copy_sequence/manifest.json`
- `logs/automated_stage_gates/stage41_pointer_copy_sequence/results.json`
- `logs/automated_stage_gates/stage41_pointer_copy_sequence/summary.csv`
- `logs/automated_stage_gates/stage41_pointer_copy_sequence/train_summary.csv`
- `logs/automated_stage_gates/stage41_pointer_copy_sequence/validation_summary.csv`
- `logs/automated_stage_gates/stage41_pointer_copy_sequence/per_run_results.csv`
- `logs/automated_stage_gates/stage41_pointer_copy_sequence/task_summary.csv`
- `logs/automated_stage_gates/stage41_pointer_copy_sequence/weak_runs.json`

## Result

The pointer/copy head repairs held-out sequence retrieval for the strongest positional methods at length `2048`:

| Method | Train top-1 | Validation top-1 | Test top-1 | Test MRR | Test target value probability | Test ECE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `rope_relative` | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.999834 | 0.000166 |
| `phasewrap_multiscale_adapter` | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.969476 | 0.038697 |
| `phasewrap_distance_adapter` | 1.000000 | 0.966667 | 0.966667 | 0.983333 | 0.948542 | 0.043022 |
| `sinusoidal` | 0.988889 | 0.750000 | 0.736666 | 0.860000 | 0.761534 | 0.128622 |
| `no_position` | 0.180000 | 0.076667 | 0.033333 | 0.132960 | 0.040492 | 0.029939 |
| `alibi` | 0.168889 | 0.070000 | 0.033333 | 0.124564 | 0.040144 | 0.031419 |

## Interpretation

Stage 41 changes the interpretation of the Stage 39/40 collapse. The all-prefix setting itself is not necessarily fatal: once value output is coupled to a pointer/copy head, `rope_relative` and `phasewrap_multiscale_adapter` both reach perfect test top-1/MRR at length `2048`, and `phasewrap_distance_adapter` is near-perfect.

This supports the hypothesis that the earlier sequence failures were largely caused by the learned value-output path and training pipeline, not simply by PhaseWrap attention features. It also preserves the probability/calibration caveat: `rope_relative` remains strongest on target value probability and ECE, while PhaseWrap multiscale is competitive on ranking but trails in calibrated probability mass.

The next useful experiment is a trainable sequence mechanism that keeps the pointer/copy benefit while removing the deterministic-copy diagnostic shortcut. Candidate directions include a learned pointer-generator mixture, shared content/value embeddings with copy supervision, or a stronger small decoder-only transformer where the positional mechanism remains the controlled variable.

## Claim Boundary

Supported:

- deterministic pointer/copy-head evidence for the all-prefix compact sequence decoder;
- evidence that copy-style value output repairs held-out sequence length generalization at `2048`;
- evidence that PhaseWrap multiscale can match RoPE-like top-1/MRR under this diagnostic, while RoPE-like scoring remains better calibrated;
- matched feature bridge, optimizer, length curriculum, parameter count, data splits, model seeds, confidence intervals, and weak-run reporting.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- a claim that PhaseWrap-RoPE is a validated RoPE replacement.
