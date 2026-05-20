# PhaseWrap-RoPE Stage 22 Long-Context Retrieval v1

Date: `2026-05-20`

## Purpose

Stage 22 extends the Stage 12 local RULER-style retrieval packet to longer contexts: `512`, `1024`, `2048`, and `4096` tokens. The target rules remain explicit passkey, multi-needle, and aggregation rules. Targets are not selected by the PhaseWrap score.

This is a deterministic no-credential positional-scoring benchmark. It is not a trained language-model benchmark and not proof that PhaseWrap-RoPE replaces RoPE.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage22_long_context_retrieval/manifest.json`
- Results: `logs/automated_stage_gates/stage22_long_context_retrieval/results.json`
- Summary CSV: `logs/automated_stage_gates/stage22_long_context_retrieval/summary.csv`
- Task summary CSV: `logs/automated_stage_gates/stage22_long_context_retrieval/task_summary.csv`
- Length summary CSV: `logs/automated_stage_gates/stage22_long_context_retrieval/length_summary.csv`
- Per-example CSV: `logs/automated_stage_gates/stage22_long_context_retrieval/per_example_results.csv`
- Runner: `scripts/run_stage22_long_context_retrieval.py`
- Implementation: `src/qrope/stage22_long_context_retrieval.py`
- Tests: `tests/test_stage22_long_context_retrieval.py`

## Reproduce

```bash
python scripts/run_stage22_long_context_retrieval.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Result

| Method | Rows | Context min | Context max | Top-1 | MRR | Mean target probability mass | Mean first relevant rank |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `sinusoidal` | 240 | 512 | 4096 | 1.000000 | 1.000000 | 0.083888 | 1.000000 |
| `rope_relative` | 240 | 512 | 4096 | 1.000000 | 1.000000 | 0.071875 | 1.000000 |
| `no_position` | 240 | 512 | 4096 | 0.041667 | 0.118602 | 0.041659 | 18.654167 |
| `phasewrap_rope_8_12` | 240 | 512 | 4096 | 0.012500 | 0.096153 | 0.021593 | 15.212500 |
| `alibi` | 240 | 512 | 4096 | 0.000000 | 0.166601 | 0.043946 | 12.150000 |

The fixed `phasewrap_rope_8_12` scoring rule fails this long-context explicit retrieval packet. RoPE-like and sinusoidal scoring solve it with top-1 `1.0` and MRR `1.0`. This strengthens the current replacement gap: the fixed 8/12 score is not sufficient for exact-offset long-context retrieval targets that are not phase-cued.

## Claim Boundary

Supported:

- deterministic long-context retrieval stress test using explicit passkey, multi-needle, and aggregation rules;
- evidence that RoPE-like and sinusoidal scoring solve this local packet through 4096-token contexts;
- evidence that the fixed PhaseWrap 8/12 score is weak on this non-phase-cued long-context packet.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next downstream experiment should be a trained small decoder-only transformer or compact retrieval model on a standard retrieval task with matched compute, multiple seeds, confidence intervals, and failed-run artifacts.
