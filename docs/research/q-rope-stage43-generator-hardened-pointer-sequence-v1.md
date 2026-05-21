# PhaseWrap-RoPE Stage 43 Generator-Hardened Pointer Sequence v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 43 tests the Stage 42 bottleneck directly: whether the learned vocab branch was weak because the high copy gate starved it of useful gradient. It keeps the Stage 40-42 all-prefix curriculum, data rows, positional-method comparison set, parameter count, and five model initialization seeds, but adds an auxiliary generator-target loss to the trainable pointer-generator.

The model still learns:

- positional attention over all prefix tokens;
- value embeddings and learned vocab projection;
- a sigmoid gate mixing copied prefix-token mass with the learned vocab distribution.

The added loss directly supervises the generator branch. This is output-path hardening inside the compact diagnostic, not a matched decoder-only transformer benchmark.

## Reviewer Command

```bash
python scripts/run_stage43_generator_hardened_pointer_sequence.py
```

This writes:

- `logs/automated_stage_gates/stage43_generator_hardened_pointer_sequence/manifest.json`
- `logs/automated_stage_gates/stage43_generator_hardened_pointer_sequence/results.json`
- `logs/automated_stage_gates/stage43_generator_hardened_pointer_sequence/summary.csv`
- `logs/automated_stage_gates/stage43_generator_hardened_pointer_sequence/train_summary.csv`
- `logs/automated_stage_gates/stage43_generator_hardened_pointer_sequence/validation_summary.csv`
- `logs/automated_stage_gates/stage43_generator_hardened_pointer_sequence/per_run_results.csv`
- `logs/automated_stage_gates/stage43_generator_hardened_pointer_sequence/task_summary.csv`
- `logs/automated_stage_gates/stage43_generator_hardened_pointer_sequence/weak_runs.json`

## Result

Generator-target hardening improves the Stage 42 learned-generator branch and raises target value probability for the strongest methods, but it does not change the RoPE-favorable ordering:

| Method | Test top-1 | Test MRR | Target value probability | Generator top-1 | Generator target probability | Copy gate | ECE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `rope_relative` | 1.000000 | 1.000000 | 0.975293 | 0.323333 | 0.315430 | 0.970862 | 0.024725 |
| `phasewrap_multiscale_adapter` | 0.970000 | 0.985000 | 0.935594 | 0.326667 | 0.309601 | 0.978397 | 0.054413 |
| `phasewrap_distance_adapter` | 0.966667 | 0.983333 | 0.924739 | 0.320000 | 0.307642 | 0.975738 | 0.046893 |
| `sinusoidal` | 0.753333 | 0.871667 | 0.754919 | 0.280000 | 0.236851 | 0.966937 | 0.099522 |
| `alibi` | 0.090000 | 0.218194 | 0.043118 | 0.016667 | 0.007558 | 0.996798 | 0.031071 |
| `no_position` | 0.076667 | 0.204035 | 0.042826 | 0.013333 | 0.007404 | 0.996200 | 0.017866 |

Compared with Stage 42, the successful methods' generator target probability moves from roughly uniform (`~0.0053`) to roughly `0.31`. The mixed output also becomes sharper: `rope_relative` target value probability rises from `0.937847` to `0.975293`; `phasewrap_distance_adapter` rises from `0.904314` to `0.924739`; `phasewrap_multiscale_adapter` rises from `0.880976` to `0.935594`.

The generator branch is still not a solved free value generator. Generator-only top-1 remains below `0.50` for every tested method, and the copy gate remains high (`~0.97-0.98`) for the successful positional methods.

## Interpretation

Stage 43 strengthens the Stage 42 diagnosis. The weak learned generator branch was partly a training-starvation issue: direct generator supervision substantially increases generator target probability. However, the learned generator still does not solve held-out value generation by itself, and the final mixture continues to rely heavily on copying.

The PhaseWrap-derived adapters remain competitive on ranking under the hardened output path, especially `phasewrap_multiscale_adapter`, but `rope_relative` remains the strongest overall method by top-1, MRR, target probability, and ECE. This keeps the honest claim boundary at `BOUND`: useful compact mechanism evidence, not replacement evidence.

The next useful move is not another small copy-route variant. Either move this fair comparison into a stronger matched decoder-only transformer or explicitly record a compact-diagnostic plateau before attempting broader claims.

## Claim Boundary

Supported:

- deterministic generator-target-hardening evidence for the all-prefix compact sequence decoder;
- evidence that auxiliary generator supervision improves the Stage 42 weak learned vocab branch;
- evidence that PhaseWrap-derived adapters remain ranking-competitive under hardened copy-aware output;
- evidence that RoPE-like scoring remains strongest on the main probability/calibration metrics;
- matched feature bridge, optimizer, length curriculum, parameter count, data splits, model seeds, confidence intervals, and weak-run reporting.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- a claim that PhaseWrap-RoPE is a validated RoPE replacement.
