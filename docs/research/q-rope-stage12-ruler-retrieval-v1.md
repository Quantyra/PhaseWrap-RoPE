# PhaseWrap-RoPE Stage 12 RULER-Style Retrieval Benchmark v1

Date: `2026-05-20`

## Purpose

Stage 12 adds a stricter no-credential retrieval benchmark for the RoPE-replacement research lane. Unlike the Stage 8 phase-cued packet, the Stage 12 targets are selected by explicit retrieval rules and RNG offsets, not by maximizing the PhaseWrap score.

This is still a local deterministic positional-scoring benchmark, not a production language-model benchmark and not proof that PhaseWrap-RoPE replaces RoPE.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage12_ruler_retrieval/manifest.json`
- Results: `logs/automated_stage_gates/stage12_ruler_retrieval/results.json`
- Summary CSV: `logs/automated_stage_gates/stage12_ruler_retrieval/summary.csv`
- Task summary CSV: `logs/automated_stage_gates/stage12_ruler_retrieval/task_summary.csv`
- Per-example CSV: `logs/automated_stage_gates/stage12_ruler_retrieval/per_example_results.csv`
- Runner: `scripts/run_stage12_ruler_retrieval.py`
- Implementation: `src/qrope/stage12_ruler_retrieval.py`
- Tests: `tests/test_stage12_ruler_retrieval.py`

## Reproduce

```bash
python scripts/run_stage12_ruler_retrieval.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Task

The fixed packet uses five seeds, context lengths `128`, `256`, `512`, and `1024`, and three task families:

- `passkey_exact`: retrieve the position at an explicit query offset.
- `multi_needle`: retrieve the third same-token occurrence in increasing delta order.
- `aggregation`: rank either of two explicit offsets selected by the aggregation packet generator.

All methods receive the same content signal and differ only in positional scoring. The compared rules are `phasewrap_rope_8_12`, `rope_relative`, `alibi`, `sinusoidal`, and `no_position`.

## Result

| Method | Rows | Lengths | Top-1 | 95% CI | MRR | 95% CI | Mean target probability mass | Mean first relevant rank |
| --- | ---: | --- | ---: | --- | ---: | --- | ---: | ---: |
| `sinusoidal` | 240 | 128-1024 | 1.000000 | 1.000000-1.000000 | 1.000000 | 1.000000-1.000000 | 0.133221 | 1.000000 |
| `rope_relative` | 240 | 128-1024 | 1.000000 | 1.000000-1.000000 | 1.000000 | 1.000000-1.000000 | 0.115837 | 1.000000 |
| `no_position` | 240 | 128-1024 | 0.079167 | 0.045833-0.116667 | 0.204656 | 0.172769-0.235219 | 0.077052 | 11.183333 |
| `phasewrap_rope_8_12` | 240 | 128-1024 | 0.020833 | 0.004167-0.041667 | 0.156865 | 0.138768-0.177360 | 0.039606 | 9.387500 |
| `alibi` | 240 | 128-1024 | 0.000000 | 0.000000-0.000000 | 0.199182 | 0.184235-0.214622 | 0.077402 | 8.466667 |

On this exact-offset retrieval packet, the RoPE-like and sinusoidal baselines solve the task, while `phasewrap_rope_8_12` does not. The benchmark therefore strengthens the evidence boundary: PhaseWrap-RoPE remains a RoPE-facing research hypothesis, not a validated replacement.

## Non-Phase-Cued Diagnostic

The packet records the fraction of rows where the explicit task target is also the best PhaseWrap-scored same-token candidate. The current overlap is `0.020833`, confirming that Stage 12 is not another PhaseWrap-oracle target packet.

## Claim Boundary

Supported:

- deterministic local retrieval comparison where targets are not defined by PhaseWrap score;
- matched scoring-rule comparison across PhaseWrap-RoPE, RoPE-like, ALiBI-like, sinusoidal, and no-position baselines;
- bootstrap intervals over top-1, MRR, and target probability mass;
- evidence that exact-offset retrieval currently favors RoPE-like/sinusoidal behavior over the fixed 8/12 PhaseWrap score.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next RoPE-facing experiment should move from local scoring rules to a stronger matched small decoder-only transformer with train-short/test-long evaluation on non-phase-cued retrieval or QA tasks, multiple seeds, failed-run artifacts, and confidence intervals.
