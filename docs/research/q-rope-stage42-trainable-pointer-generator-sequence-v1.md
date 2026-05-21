# PhaseWrap-RoPE Stage 42 Trainable Pointer-Generator Sequence v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 42 tests whether the Stage 41 pointer/copy repair survives when the output path is trainable. It keeps the Stage 40/41 curriculum, all-prefix token competition, feature bridge, and five model initialization seeds, but replaces the deterministic copy-only value output with a trainable pointer-generator mixture.

The model learns:

- positional attention over all prefix tokens;
- value embeddings and a learned vocab projection;
- a sigmoid gate that mixes copied prefix-token mass with the learned vocab distribution.

This is still a compact diagnostic, not a production decoder-only transformer benchmark.

## Reviewer Command

```bash
python scripts/run_stage42_trainable_pointer_generator_sequence.py
```

This writes:

- `logs/automated_stage_gates/stage42_trainable_pointer_generator_sequence/manifest.json`
- `logs/automated_stage_gates/stage42_trainable_pointer_generator_sequence/results.json`
- `logs/automated_stage_gates/stage42_trainable_pointer_generator_sequence/summary.csv`
- `logs/automated_stage_gates/stage42_trainable_pointer_generator_sequence/train_summary.csv`
- `logs/automated_stage_gates/stage42_trainable_pointer_generator_sequence/validation_summary.csv`
- `logs/automated_stage_gates/stage42_trainable_pointer_generator_sequence/per_run_results.csv`
- `logs/automated_stage_gates/stage42_trainable_pointer_generator_sequence/task_summary.csv`
- `logs/automated_stage_gates/stage42_trainable_pointer_generator_sequence/weak_runs.json`

## Result

The trainable pointer-generator preserves most of the Stage 41 sequence repair, but not the full copy-head probability level:

| Method | Train top-1 | Validation top-1 | Test top-1 | Test MRR | Test target value probability | Test copy gate | Test ECE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `rope_relative` | 1.000000 | 0.983333 | 1.000000 | 1.000000 | 0.937847 | 0.938914 | 0.062211 |
| `phasewrap_distance_adapter` | 1.000000 | 0.956667 | 0.966667 | 0.983333 | 0.904314 | 0.957437 | 0.077651 |
| `phasewrap_multiscale_adapter` | 1.000000 | 1.000000 | 0.946667 | 0.973333 | 0.880976 | 0.935214 | 0.097450 |
| `sinusoidal` | 0.952222 | 0.820000 | 0.763333 | 0.878889 | 0.727549 | 0.946476 | 0.131095 |
| `alibi` | 0.132223 | 0.090000 | 0.086667 | 0.213817 | 0.042753 | 0.992436 | 0.027323 |
| `no_position` | 0.161111 | 0.100000 | 0.070000 | 0.197315 | 0.042548 | 0.992051 | 0.010117 |

The learned vocab branch remains weak by itself: mean generator target probability is near `0.0053` for the successful positional methods, close to uniform over the `257`-token value vocabulary. The learned gate therefore mostly preserves the copy route; it does not yet solve free learned value generation.

## Interpretation

Stage 42 strengthens the Stage 41 diagnosis. The sequence-length collapse in Stages 39/40 was not caused solely by all-prefix competition: once the model has a copy-aware output path, RoPE-like scoring and both PhaseWrap-derived adapters recover strong `2048`-token ranking.

The ordering is still RoPE-favorable. `rope_relative` has perfect test top-1/MRR and the strongest target probability/ECE. `phasewrap_distance_adapter` is near-perfect on ranking, while `phasewrap_multiscale_adapter` remains high but loses the perfect ranking it had under deterministic copy output.

The key bottleneck has moved: attention plus copy-style value coupling is viable, but the learned generator branch contributes little target mass. The next useful step is to harden the trainable output mechanism, either by calibrating/sharpening the copy gate, adding copy supervision, or moving this pointer-generator idea into a stronger small decoder-only transformer with matched positional controls.

## Claim Boundary

Supported:

- deterministic trainable pointer-generator evidence for the all-prefix compact sequence decoder;
- evidence that learned copy/vocab mixing preserves much of the Stage 41 sequence-length repair;
- evidence that PhaseWrap-derived adapters remain competitive on ranking under trainable copy-aware output, while RoPE-like scoring remains best on probability/calibration;
- matched feature bridge, optimizer, length curriculum, parameter count, data splits, model seeds, confidence intervals, and weak-run reporting.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- a claim that PhaseWrap-RoPE is a validated RoPE replacement.
