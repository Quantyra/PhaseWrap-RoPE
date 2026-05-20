# PhaseWrap-RoPE Stage 13 Positional-Adapter Benchmark v1

Date: `2026-05-20`

## Purpose

Stage 13 tests whether a trained PhaseWrap-derived positional adapter can close the Stage 12 non-phase-cued retrieval gap. It reuses the Stage 12 passkey, multi-needle, and aggregation-style packet, trains on short contexts, and evaluates on held-out length-1024 rows.

This is a local positional-adapter benchmark. It is not a production transformer benchmark and not proof that PhaseWrap-RoPE replaces RoPE.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage13_positional_adapter/manifest.json`
- Results: `logs/automated_stage_gates/stage13_positional_adapter/results.json`
- Summary CSV: `logs/automated_stage_gates/stage13_positional_adapter/summary.csv`
- Task summary CSV: `logs/automated_stage_gates/stage13_positional_adapter/task_summary.csv`
- Runner: `scripts/run_stage13_positional_adapter.py`
- Implementation: `src/qrope/stage13_positional_adapter.py`
- Tests: `tests/test_stage13_positional_adapter.py`

## Reproduce

```bash
python scripts/run_stage13_positional_adapter.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Task

The benchmark trains lightweight positional adapters on Stage 12 rows with context lengths `128` and `256`, keeps length `512` as a declared validation length, and evaluates on length `1024`.

The compared mechanisms are:

- `no_position`
- `alibi`
- `rope_relative`
- `sinusoidal`
- `phasewrap_score`
- `phasewrap_residual_adapter`
- `phasewrap_distance_adapter`

The `phasewrap_score` method uses only the fixed 8/12 score plus intercept. The residual adapter adds wrapped residual features. The distance adapter adds normalized signed and absolute distance terms around the PhaseWrap residual features.

## Result

| Method | Test rows | Top-1 | 95% CI | MRR | 95% CI | Mean target probability mass | Mean first relevant rank |
| --- | ---: | ---: | --- | ---: | --- | ---: | ---: |
| `rope_relative` | 60 | 1.000000 | 1.000000-1.000000 | 1.000000 | 1.000000-1.000000 | 0.821549 | 1.000000 |
| `phasewrap_distance_adapter` | 60 | 1.000000 | 1.000000-1.000000 | 1.000000 | 1.000000-1.000000 | 0.429105 | 1.000000 |
| `sinusoidal` | 60 | 0.666667 | 0.533333-0.766667 | 0.825000 | 0.763889-0.888889 | 0.381731 | 1.383333 |
| `phasewrap_residual_adapter` | 60 | 0.450000 | 0.333333-0.583333 | 0.673611 | 0.597222-0.747222 | 0.260873 | 1.900000 |
| `no_position` | 60 | 0.050000 | 0.000000-0.100000 | 0.118035 | 0.069565-0.177490 | 0.037879 | 21.016667 |
| `phasewrap_score` | 60 | 0.016667 | 0.000000-0.050000 | 0.080860 | 0.059071-0.123087 | 0.044468 | 16.766667 |
| `alibi` | 60 | 0.000000 | 0.000000-0.000000 | 0.153196 | 0.121164-0.185813 | 0.038645 | 13.900000 |

The fixed score alone remains weak on exact-offset retrieval. The `phasewrap_residual_adapter` improves ranking but does not solve the packet. The `phasewrap_distance_adapter` matches `rope_relative` on top-1 and MRR across the held-out length-1024 rows, but `rope_relative` has higher target probability mass. This is a useful mechanism clue, not a replacement result.

## Claim Boundary

Supported:

- deterministic train-short/test-long positional-adapter comparison on non-phase-cued retrieval rows;
- evidence that PhaseWrap residual features alone do not close the exact-offset gap;
- evidence that adding explicit distance features to PhaseWrap residual features can close argmax ranking on this local packet;
- bootstrap intervals over held-out test rows.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next downstream experiment should put the successful adapter shape into a stronger small decoder-only transformer, preserve matched compute and seeds, and evaluate on non-phase-cued retrieval or compact QA tasks with failed-run artifacts.
