# PhaseWrap-RoPE Stage 21 Hardened Positional Stability v1

Date: `2026-05-20`

## Purpose

Stage 21 reruns the Stage 20 hardened positional value-model benchmark across five learned-parameter initialization seeds. It tests whether the Stage 20 held-out ordering is stable or only a single-initialization artifact.

This is a local multi-initialization stability benchmark. It is not a production transformer benchmark and not proof that PhaseWrap-RoPE replaces RoPE.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage21_hardened_positional_stability/manifest.json`
- Results: `logs/automated_stage_gates/stage21_hardened_positional_stability/results.json`
- Summary CSV: `logs/automated_stage_gates/stage21_hardened_positional_stability/summary.csv`
- Per-run CSV: `logs/automated_stage_gates/stage21_hardened_positional_stability/per_run_results.csv`
- Runner: `scripts/run_stage21_hardened_positional_stability.py`
- Implementation: `src/qrope/stage21_hardened_positional_stability.py`
- Tests: `tests/test_stage21_hardened_positional_stability.py`

## Reproduce

```bash
python scripts/run_stage21_hardened_positional_stability.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Result

| Method | Runs | Top-1 mean | Top-1 min | Top-1 max | MRR mean | MRR min | MRR max | Mean target value probability |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `rope_relative` | 5 | 0.376666 | 0.350000 | 0.383333 | 0.421212 | 0.393652 | 0.438514 | 0.351668 |
| `sinusoidal` | 5 | 0.286667 | 0.250000 | 0.333333 | 0.343805 | 0.325168 | 0.374209 | 0.202451 |
| `phasewrap_distance_adapter` | 5 | 0.286667 | 0.250000 | 0.316667 | 0.339284 | 0.313002 | 0.355248 | 0.205887 |
| `phasewrap_residual_adapter` | 5 | 0.216667 | 0.200000 | 0.233333 | 0.283518 | 0.267908 | 0.297993 | 0.134418 |
| `no_position` | 5 | 0.020000 | 0.000000 | 0.033333 | 0.058333 | 0.045613 | 0.067669 | 0.009042 |
| `alibi` | 5 | 0.010000 | 0.000000 | 0.033333 | 0.041017 | 0.028398 | 0.071416 | 0.006960 |
| `phasewrap_score` | 5 | 0.006667 | 0.000000 | 0.016667 | 0.040120 | 0.032366 | 0.047294 | 0.008622 |

The Stage 20 ordering is stable across the tested initialization seeds: `rope_relative` remains strongest by mean held-out top-1 and MRR. `phasewrap_distance_adapter` is close to `sinusoidal` on mean top-1, but trails both `rope_relative` and `sinusoidal` on mean MRR. The fixed `phasewrap_score` remains weak.

## Claim Boundary

Supported:

- deterministic five-initialization stability check for the Stage 20 local benchmark;
- evidence that the RoPE-like held-out advantage over the tested PhaseWrap adapters is stable on this packet;
- evidence that PhaseWrap-plus-distance remains a candidate adapter shape, but not the best tested method here.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next downstream experiment should leave the local Stage 14 packet and move to a stronger small decoder-only transformer or standard retrieval benchmark with matched compute, multiple seeds, and reported failed or negative runs.
