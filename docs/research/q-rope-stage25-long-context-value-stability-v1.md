# PhaseWrap-RoPE Stage 25 Long-Context Value Stability v1

Date: `2026-05-20`

## Purpose

Stage 25 reruns the Stage 24 long-context value-model benchmark across five learned-parameter initialization seeds. It is a deterministic stability check for the compact value-retrieval model, not a new hardware run and not a full transformer benchmark.

The benchmark uses the same explicit Stage 22 passkey, multi-needle, and aggregation target rules. Targets are not selected by the PhaseWrap score.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage25_long_context_value_stability/manifest.json`
- Results: `logs/automated_stage_gates/stage25_long_context_value_stability/results.json`
- Summary CSV: `logs/automated_stage_gates/stage25_long_context_value_stability/summary.csv`
- Per-run CSV: `logs/automated_stage_gates/stage25_long_context_value_stability/per_run_results.csv`
- Weak-run records: `logs/automated_stage_gates/stage25_long_context_value_stability/weak_run_records.json`
- Runner: `scripts/run_stage25_long_context_value_stability.py`
- Implementation: `src/qrope/stage25_long_context_value_stability.py`
- Tests: `tests/test_stage25_long_context_value_stability.py`

## Reproduce

```bash
python scripts/run_stage25_long_context_value_stability.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Result

| Method | Runs | Top-1 mean | Top-1 range | MRR mean | MRR range | Mean target value probability |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `rope_relative` | 5 | 0.383333 | 0.350000-0.433333 | 0.426498 | 0.399642-0.449010 | 0.362492 |
| `sinusoidal` | 5 | 0.140000 | 0.000000-0.233333 | 0.195098 | 0.020441-0.303537 | 0.129313 |
| `phasewrap_residual_adapter` | 5 | 0.073333 | 0.016667-0.150000 | 0.120739 | 0.048489-0.224397 | 0.055600 |
| `phasewrap_distance_adapter` | 5 | 0.056667 | 0.000000-0.266667 | 0.087324 | 0.018217-0.312769 | 0.047178 |
| `alibi` | 5 | 0.020000 | 0.000000-0.050000 | 0.050738 | 0.038682-0.076180 | 0.009690 |
| `no_position` | 5 | 0.016667 | 0.000000-0.066667 | 0.053413 | 0.033871-0.102984 | 0.010921 |
| `phasewrap_score` | 5 | 0.006667 | 0.000000-0.016667 | 0.035437 | 0.023524-0.046642 | 0.007448 |

`rope_relative` is the strongest method across the tested initialization seeds. The strongest PhaseWrap-derived method is `phasewrap_residual_adapter`, but it remains behind `rope_relative` by mean top-1, MRR, and target value probability.

This is useful negative/mixed evidence for the current PhaseWrap-derived long-context value-model path. It does not close the RoPE-replacement gap.

## Claim Boundary

Supported:

- deterministic multi-initialization stability evidence for the Stage 24 compact value-retrieval model;
- evidence that the Stage 24 RoPE-like held-out advantage persists across the tested initialization seeds;
- reported weak runs under a predeclared top-1 threshold.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next downstream experiment should leave the compact value-retrieval setup and move to a stronger small decoder-only transformer or standard retrieval/QA task with matched compute, multiple seeds, confidence intervals, and failed-run artifacts.
