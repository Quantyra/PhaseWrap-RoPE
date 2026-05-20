# PhaseWrap-RoPE Stage 20 Hardened Positional Value Model v1

Date: `2026-05-20`

## Purpose

Stage 20 reintroduces learned positional attention after the Stage 19 value-output hardening probe. It uses the Stage 14 non-phase-cued key-value rows, trains attention weights for each positional feature family, and keeps the hardened full-batch Adam value-output path.

This is a local learned positional-attention/value-output comparison. It is not a production transformer benchmark and not proof that PhaseWrap-RoPE replaces RoPE.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage20_hardened_positional_value_model/manifest.json`
- Results: `logs/automated_stage_gates/stage20_hardened_positional_value_model/results.json`
- Summary CSV: `logs/automated_stage_gates/stage20_hardened_positional_value_model/summary.csv`
- Task summary CSV: `logs/automated_stage_gates/stage20_hardened_positional_value_model/task_summary.csv`
- Runner: `scripts/run_stage20_hardened_positional_value_model.py`
- Implementation: `src/qrope/stage20_hardened_positional_value_model.py`
- Tests: `tests/test_stage20_hardened_positional_value_model.py`

## Reproduce

```bash
python scripts/run_stage20_hardened_positional_value_model.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Held-Out Result

| Method | Test rows | Top-1 | MRR | Mean target value probability | Mean first relevant value rank |
| --- | ---: | ---: | ---: | ---: | ---: |
| `rope_relative` | 60 | 0.383333 | 0.429275 | 0.350653 | 78.200000 |
| `sinusoidal` | 60 | 0.300000 | 0.338548 | 0.192121 | 89.116667 |
| `phasewrap_distance_adapter` | 60 | 0.250000 | 0.321470 | 0.193673 | 76.300000 |
| `phasewrap_residual_adapter` | 60 | 0.233333 | 0.295736 | 0.141399 | 74.233333 |
| `alibi` | 60 | 0.033333 | 0.071416 | 0.009900 | 111.716667 |
| `no_position` | 60 | 0.033333 | 0.067669 | 0.009756 | 96.533333 |
| `phasewrap_score` | 60 | 0.000000 | 0.032774 | 0.006122 | 100.166667 |

All methods fit the 120 training rows with top-1 `1.0` and MRR `1.0`, so this stage is not blocked by the Stage 17/18 value-output failure. On held-out length-1024 rows, `rope_relative` is strongest. PhaseWrap-derived adapters outperform the fixed PhaseWrap score and the no-position/ALiBI baselines, but they do not beat RoPE-like scoring on this packet.

## Claim Boundary

Supported:

- deterministic local comparison of learned positional feature families using the hardened value-output path;
- evidence that the hardened path resolves train-fit failure from Stages 17 and 18;
- evidence that PhaseWrap-plus-distance remains worth testing, but trails RoPE-like scoring on this non-phase-cued held-out packet.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next downstream experiment should move from this local learned-attention/value-output comparison to a stronger small decoder-only transformer or a standard retrieval benchmark with multiple seeds, matched compute, and confidence intervals. The result should be expected to include failed or negative PhaseWrap runs if RoPE remains stronger.
