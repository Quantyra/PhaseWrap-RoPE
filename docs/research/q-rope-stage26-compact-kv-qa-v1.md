# PhaseWrap-RoPE Stage 26 Compact Key-Value QA v1

Date: `2026-05-20`

## Purpose

Stage 26 adds a compact key-value QA/retrieval benchmark with explicit content keys, distractor facts, and train-short/test-long context lengths. The target is the latest candidate whose key matches the query key. Targets are not selected by the PhaseWrap score.

This is a deterministic local compact retrieval benchmark. It is not a full transformer benchmark and not proof that PhaseWrap-RoPE replaces RoPE.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage26_compact_kv_qa/manifest.json`
- Results: `logs/automated_stage_gates/stage26_compact_kv_qa/results.json`
- Summary CSV: `logs/automated_stage_gates/stage26_compact_kv_qa/summary.csv`
- Weak-run records: `logs/automated_stage_gates/stage26_compact_kv_qa/weak_runs.json`
- Runner: `scripts/run_stage26_compact_kv_qa.py`
- Implementation: `src/qrope/stage26_compact_kv_qa.py`
- Tests: `tests/test_stage26_compact_kv_qa.py`

## Reproduce

```bash
python scripts/run_stage26_compact_kv_qa.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Result

| Method | Test rows | Top-1 | MRR | Mean target probability | Mean first relevant rank |
| --- | ---: | ---: | ---: | ---: | ---: |
| `alibi` | 20 | 0.950000 | 0.975000 | 0.729148 | 1.050000 |
| `phasewrap_residual_adapter` | 20 | 0.950000 | 0.975000 | 0.712015 | 1.050000 |
| `phasewrap_distance_adapter` | 20 | 0.950000 | 0.975000 | 0.767915 | 1.050000 |
| `sinusoidal` | 20 | 0.900000 | 0.950000 | 0.652003 | 1.100000 |
| `rope_relative` | 20 | 0.500000 | 0.716667 | 0.495112 | 1.700000 |
| `phasewrap_score` | 20 | 0.300000 | 0.608333 | 0.325043 | 1.950000 |
| `no_position` | 20 | 0.000000 | 0.325000 | 0.315454 | 3.100000 |

The strongest methods by test top-1/MRR are `alibi`, `phasewrap_residual_adapter`, and `phasewrap_distance_adapter`. Among those tied methods, `phasewrap_distance_adapter` has the highest mean target probability. The fixed `phasewrap_score` remains weak.

This supports continued study of PhaseWrap-derived adapters in compact retrieval settings with explicit content keys. It does not override Stage 24 or Stage 25, where the learned long-context value-output path favored RoPE-like scoring.

## Claim Boundary

Supported:

- deterministic compact key-value QA/retrieval evidence with explicit content keys;
- evidence that PhaseWrap-derived adapters can match ALiBI-style top-1/MRR on this packet;
- evidence that fixed PhaseWrap scoring remains insufficient on this packet.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next downstream experiment should put this content-key retrieval structure into a stronger small decoder-only transformer with matched parameter counts, optimizer settings, training tokens, multiple seeds, confidence intervals, and failed-run artifacts.
