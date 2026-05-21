# PhaseWrap-RoPE Stage 40 Sequence Length Curriculum v1

Date: `2026-05-20`

Status: `completed`

## Purpose

Stage 40 tests whether the Stage 39 all-prefix sequence decoder failure is mainly caused by too narrow a train-length curriculum. It keeps the same compact sequence decoder with all prefix tokens competing, but trains on lengths `128`, `256`, and `512`, validates on `1024`, and tests on `2048`.

This is a length-generalization repair attempt, not a new RoPE-replacement claim.

## Reviewer Command

```bash
python scripts/run_stage40_sequence_length_curriculum.py
```

This writes:

- `logs/automated_stage_gates/stage40_sequence_length_curriculum/manifest.json`
- `logs/automated_stage_gates/stage40_sequence_length_curriculum/results.json`
- `logs/automated_stage_gates/stage40_sequence_length_curriculum/summary.csv`
- `logs/automated_stage_gates/stage40_sequence_length_curriculum/train_summary.csv`
- `logs/automated_stage_gates/stage40_sequence_length_curriculum/validation_summary.csv`
- `logs/automated_stage_gates/stage40_sequence_length_curriculum/per_run_results.csv`
- `logs/automated_stage_gates/stage40_sequence_length_curriculum/task_summary.csv`
- `logs/automated_stage_gates/stage40_sequence_length_curriculum/weak_runs.json`

## Result

The length curriculum does not repair held-out length extrapolation. The PhaseWrap-derived adapters have the strongest `2048`-length test rows, but the absolute numbers remain near chance:

| Method | Train top-1 | Validation top-1 | Test top-1 | Test MRR | Test target value probability |
| --- | ---: | ---: | ---: | ---: | ---: |
| `phasewrap_distance_adapter` | 0.954444 | 0.000000 | 0.030000 | 0.060933 | 0.020555 |
| `phasewrap_multiscale_adapter` | 0.972222 | 0.000000 | 0.023333 | 0.058393 | 0.019660 |
| `sinusoidal` | 0.954444 | 0.013334 | 0.020000 | 0.054044 | 0.014491 |
| `alibi` | 0.441111 | 0.003333 | 0.006667 | 0.035444 | 0.007012 |
| `rope_relative` | 0.857778 | 0.003333 | 0.006667 | 0.031473 | 0.005798 |
| `no_position` | 0.452222 | 0.016667 | 0.003333 | 0.027284 | 0.005225 |

## Interpretation

Stage 40 gives a narrow but useful answer: adding length `512` to the training curriculum is not enough to make the compact all-prefix sequence decoder generalize to `1024` or `2048`.

The result is not a clean PhaseWrap win because all absolute held-out scores remain weak. It does show that, under this failed extrapolation regime, the PhaseWrap-derived adapters rank above `rope_relative` on the `2048` test rows. The stronger conclusion is still architectural: the current compact sequence decoder does not yet provide a reliable promotion harness for positional-method comparison.

The next useful step should change the sequence training mechanism, not merely add another comparison. Candidate directions include stronger length normalization, attention-temperature selection by validation length, copy-assisted or pointer-style value output, or a more RoPE-comparable PhaseWrap rotation/bias mechanism.

## Claim Boundary

Supported:

- deterministic length-curriculum evidence for the all-prefix compact sequence decoder;
- evidence that training on `128`/`256`/`512` does not repair held-out `1024`/`2048` generalization;
- evidence that PhaseWrap-derived adapters are the strongest tested variants on the weak `2048` test rows;
- matched architecture, optimizer, parameter count, data splits, model seeds, confidence intervals, and weak-run reporting.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- a claim that PhaseWrap-RoPE is a validated RoPE replacement.
