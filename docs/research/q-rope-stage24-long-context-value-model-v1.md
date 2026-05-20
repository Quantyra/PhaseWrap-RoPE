# PhaseWrap-RoPE Stage 24 Long-Context Value Model v1

Date: `2026-05-20`

## Purpose

Stage 24 adds a compact learned value-retrieval model on the explicit long-context rows introduced in Stage 22. It uses learned positional attention, learned value embeddings, and an output projection. The split is train on `512` and `1024` token contexts, validate on `2048`, and test on `4096`.

Targets remain explicit passkey, multi-needle, and aggregation rules. They are not selected by the PhaseWrap score. This is a deterministic local compact retrieval model, not a full transformer benchmark and not proof that PhaseWrap-RoPE replaces RoPE.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage24_long_context_value_model/manifest.json`
- Results: `logs/automated_stage_gates/stage24_long_context_value_model/results.json`
- Summary CSV: `logs/automated_stage_gates/stage24_long_context_value_model/summary.csv`
- Task summary CSV: `logs/automated_stage_gates/stage24_long_context_value_model/task_summary.csv`
- Runner: `scripts/run_stage24_long_context_value_model.py`
- Implementation: `src/qrope/stage24_long_context_value_model.py`
- Tests: `tests/test_stage24_long_context_value_model.py`

## Reproduce

```bash
python scripts/run_stage24_long_context_value_model.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Result

| Method | Test rows | Top-1 | MRR | Mean target value probability | Mean first relevant value rank |
| --- | ---: | ---: | ---: | ---: | ---: |
| `rope_relative` | 60 | 0.350000 | 0.399642 | 0.362745 | 84.533333 |
| `phasewrap_residual_adapter` | 60 | 0.133333 | 0.221899 | 0.118677 | 89.700000 |
| `sinusoidal` | 60 | 0.033333 | 0.064218 | 0.012284 | 105.683333 |
| `phasewrap_distance_adapter` | 60 | 0.016667 | 0.051084 | 0.007212 | 105.283333 |
| `alibi` | 60 | 0.016667 | 0.046827 | 0.008462 | 102.066667 |
| `phasewrap_score` | 60 | 0.016667 | 0.046642 | 0.010065 | 111.816667 |
| `no_position` | 60 | 0.000000 | 0.033871 | 0.006736 | 104.850000 |

All methods fit the training rows at top-1 `1.000000` and MRR `1.000000`, but the held-out `4096` token value-retrieval rows favor `rope_relative`. `phasewrap_residual_adapter` is the strongest PhaseWrap-derived method on this packet, while `phasewrap_distance_adapter` does not preserve its Stage 23 argmax result after the learned value-output path is added.

This is useful negative/mixed evidence. It narrows the RoPE-replacement gap: the adapter that solved Stage 23 positional ranking is not sufficient once value-token learning and output projection are included.

## Claim Boundary

Supported:

- deterministic compact value-retrieval model over explicit long-context retrieval rows;
- evidence that all tested positional mechanisms can fit train under the current learned value-output path;
- evidence that `rope_relative` is strongest on held-out `4096` token value retrieval in this packet;
- evidence that the current PhaseWrap-derived adapters remain behind RoPE-like scoring once value-token learning is included.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next downstream experiment should move from this compact value-retrieval model to a stronger small decoder-only transformer or compact standard retrieval/QA setup with multiple initialization seeds, confidence intervals across runs, and failed-run artifacts.
