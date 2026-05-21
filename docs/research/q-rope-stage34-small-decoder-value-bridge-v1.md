# PhaseWrap-RoPE Stage 34 Small Decoder Value Bridge v1

Date: `2026-05-20`

Status: `completed`

## Purpose

Stage 34 moves the Stage 32/33 full-context retrieval signal into a stronger compact decoder-style value bridge. The benchmark uses Stage 14 key-value rows derived from Stage 12 non-phase-cued retrieval examples. The model trains a nonlinear positional attention bridge plus learned value embeddings and a learned output projection, so success requires the selected position to survive a value-token output bottleneck.

Targets are explicit retrieval-rule value tokens, not PhaseWrap-generated labels.

## Reviewer Command

```bash
python scripts/run_stage34_small_decoder_value_bridge.py
```

This writes:

- `logs/automated_stage_gates/stage34_small_decoder_value_bridge/manifest.json`
- `logs/automated_stage_gates/stage34_small_decoder_value_bridge/results.json`
- `logs/automated_stage_gates/stage34_small_decoder_value_bridge/summary.csv`
- `logs/automated_stage_gates/stage34_small_decoder_value_bridge/per_run_results.csv`
- `logs/automated_stage_gates/stage34_small_decoder_value_bridge/task_summary.csv`
- `logs/automated_stage_gates/stage34_small_decoder_value_bridge/weak_runs.json`

## Design

Every method uses:

- the same Stage 14 train/validation/test split;
- five deterministic model initialization seeds;
- the same nonlinear attention bridge width;
- the same learned value embedding dimension;
- the same output projection, optimizer, epochs, and parameter count;
- confidence intervals over model initialization seeds;
- explicit weak-run reporting.

## Result

On the default artifact, `rope_relative` is strongest in the compact value-output setting:

| Method | Top-1 | MRR | Mean target value probability | ECE |
| --- | ---: | ---: | ---: | ---: |
| `rope_relative` | 0.360000 | 0.403972 | 0.345612 | 0.200296 |
| `sinusoidal` | 0.313333 | 0.368166 | 0.293361 | 0.175060 |
| `phasewrap_distance_adapter` | 0.283333 | 0.333489 | 0.244297 | 0.207237 |
| `phasewrap_multiscale_adapter` | 0.253333 | 0.313192 | 0.204815 | 0.209341 |
| `alibi` | 0.003333 | 0.031067 | 0.005460 | 0.271258 |
| `no_position` | 0.000000 | 0.034697 | 0.005769 | 0.262192 |

## Interpretation

Stage 34 is mixed-to-negative for the current PhaseWrap-derived adapters. The adapters remain substantially above no-position and ALiBI controls, but they trail `rope_relative` and `sinusoidal` once the task requires learned value-token output rather than only positional ranking.

This is useful evidence because it narrows the next research target: the PhaseWrap mechanism must improve value-output survival and probability mass, not just recover argmax retrieval in a feature bridge.

## Claim Boundary

Supported:

- deterministic compact decoder-style value benchmark on non-phase-cued retrieval rows;
- evidence that `rope_relative` remains strongest under this value-output bridge;
- evidence that current PhaseWrap-derived adapters trail RoPE-like scoring on this packet;
- matched architecture, optimizer, parameter count, data splits, confidence intervals, and weak-run reporting.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- a claim that PhaseWrap-RoPE is a validated RoPE replacement.
