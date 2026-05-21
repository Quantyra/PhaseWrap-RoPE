# PhaseWrap-RoPE Stage 39 Sequence Decoder Retrieval v1

Date: `2026-05-20`

Status: `completed`

## Purpose

Stage 39 moves beyond candidate-only bridge supervision. It converts the Stage 14 key-value rows into a sequence-style decoder retrieval diagnostic where every prefix token competes for attention, then predicts the target value token through learned token/value embeddings and an output projection.

This tests whether the PhaseWrap-derived mechanisms survive all-prefix sequence competition with learned value output.

## Reviewer Command

```bash
python scripts/run_stage39_sequence_decoder_retrieval.py
```

This writes:

- `logs/automated_stage_gates/stage39_sequence_decoder_retrieval/manifest.json`
- `logs/automated_stage_gates/stage39_sequence_decoder_retrieval/results.json`
- `logs/automated_stage_gates/stage39_sequence_decoder_retrieval/summary.csv`
- `logs/automated_stage_gates/stage39_sequence_decoder_retrieval/train_summary.csv`
- `logs/automated_stage_gates/stage39_sequence_decoder_retrieval/validation_summary.csv`
- `logs/automated_stage_gates/stage39_sequence_decoder_retrieval/per_run_results.csv`
- `logs/automated_stage_gates/stage39_sequence_decoder_retrieval/task_summary.csv`
- `logs/automated_stage_gates/stage39_sequence_decoder_retrieval/weak_runs.json`

## Result

Several methods fit the short train rows, but all methods are near chance on held-out full-prefix length extrapolation:

| Method | Train top-1 | Test top-1 | Test MRR | Test target value probability |
| --- | ---: | ---: | ---: | ---: |
| `no_position` | 0.518334 | 0.013334 | 0.037937 | 0.007857 |
| `rope_relative` | 0.935000 | 0.010000 | 0.039489 | 0.007312 |
| `sinusoidal` | 0.935000 | 0.010000 | 0.028541 | 0.008371 |
| `alibi` | 0.530000 | 0.006667 | 0.032206 | 0.006865 |
| `phasewrap_multiscale_adapter` | 0.973334 | 0.003333 | 0.028140 | 0.003543 |
| `phasewrap_distance_adapter` | 0.951667 | 0.000000 | 0.025395 | 0.003759 |

## Interpretation

Stage 39 is negative for the current compact sequence-level decoder formulation. It is not a RoPE win: `rope_relative` also collapses on held-out length. The key result is broader: all-prefix sequence competition plus learned value output is much harder than the candidate-only bridge or copy-value bridge.

The training rows show the model can learn the short-context packet for several positional variants, especially `phasewrap_multiscale_adapter`, `phasewrap_distance_adapter`, `rope_relative`, and `sinusoidal`. The validation and test rows show that this learned solution does not extrapolate to longer full-prefix contexts.

This means the next useful work should focus on generalization mechanics, not more evidence that the current compact decoder is weak. Candidate directions include stronger sequence training across more lengths, explicit length-normalized attention calibration, or a more RoPE-comparable PhaseWrap rotation/bias mechanism.

## Claim Boundary

Supported:

- deterministic sequence-level decoder retrieval evidence on non-phase-cued Stage 14 rows;
- evidence that all-prefix token competition causes severe held-out length generalization failure for the current compact decoder formulation;
- evidence that PhaseWrap-derived adapters can fit short train rows but do not extrapolate in this setup;
- matched architecture, optimizer, parameter count, data splits, model seeds, confidence intervals, and weak-run reporting.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- a claim that PhaseWrap-RoPE is a validated RoPE replacement.
