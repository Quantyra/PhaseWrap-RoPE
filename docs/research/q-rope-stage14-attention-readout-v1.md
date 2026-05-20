# PhaseWrap-RoPE Stage 14 Attention-Readout Benchmark v1

Date: `2026-05-20`

## Purpose

Stage 14 moves the Stage 13 positional-adapter result one step closer to transformer behavior by turning the non-phase-cued retrieval rows into key-value attention-readout rows. The model ranks candidate key positions, aggregates probability onto value tokens, and is evaluated on whether the target value token is recovered.

This is still a local attention-readout benchmark. It is not a production transformer benchmark and not proof that PhaseWrap-RoPE replaces RoPE.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage14_attention_readout/manifest.json`
- Results: `logs/automated_stage_gates/stage14_attention_readout/results.json`
- Summary CSV: `logs/automated_stage_gates/stage14_attention_readout/summary.csv`
- Task summary CSV: `logs/automated_stage_gates/stage14_attention_readout/task_summary.csv`
- Runner: `scripts/run_stage14_attention_readout.py`
- Implementation: `src/qrope/stage14_attention_readout.py`
- Tests: `tests/test_stage14_attention_readout.py`

## Reproduce

```bash
python scripts/run_stage14_attention_readout.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Task

Stage 14 derives key-value rows from the Stage 12 passkey, multi-needle, and aggregation-style tasks. Targets remain explicit retrieval-rule targets, not PhaseWrap-selected positions. The benchmark trains on context lengths `128` and `256`, declares length `512` as validation, and evaluates on length `1024`.

The compared mechanisms are:

- `no_position`
- `alibi`
- `rope_relative`
- `sinusoidal`
- `phasewrap_score`
- `phasewrap_residual_adapter`
- `phasewrap_distance_adapter`

## Result

| Method | Test rows | Top-1 | 95% CI | MRR | 95% CI | Mean target value probability | Mean first relevant value rank |
| --- | ---: | ---: | --- | ---: | --- | ---: | ---: |
| `rope_relative` | 60 | 1.000000 | 1.000000-1.000000 | 1.000000 | 1.000000-1.000000 | 0.824888 | 1.000000 |
| `phasewrap_distance_adapter` | 60 | 1.000000 | 1.000000-1.000000 | 1.000000 | 1.000000-1.000000 | 0.432405 | 1.000000 |
| `sinusoidal` | 60 | 0.733333 | 0.616667-0.833333 | 0.859722 | 0.802778-0.913889 | 0.386298 | 1.316667 |
| `phasewrap_residual_adapter` | 60 | 0.500000 | 0.383333-0.616667 | 0.718056 | 0.640278-0.800000 | 0.266586 | 1.716667 |
| `alibi` | 60 | 0.100000 | 0.016667-0.166667 | 0.214748 | 0.153077-0.289779 | 0.043489 | 12.216667 |
| `no_position` | 60 | 0.083333 | 0.016667-0.166667 | 0.195125 | 0.127224-0.268153 | 0.042635 | 14.466667 |
| `phasewrap_score` | 60 | 0.050000 | 0.000000-0.100000 | 0.147274 | 0.091964-0.217219 | 0.050010 | 14.300000 |

The attention-readout result preserves the Stage 13 pattern. The fixed PhaseWrap score remains weak. Residual features improve retrieval. PhaseWrap plus distance matches RoPE-like scoring on top-1 and MRR for this held-out packet, but RoPE-like scoring has much higher target value probability. The appropriate interpretation is that PhaseWrap-derived features may be useful as an adapter component, not that the current method replaces RoPE.

## Claim Boundary

Supported:

- deterministic train-short/test-long attention-readout comparison on non-phase-cued key-value retrieval rows;
- evidence that fixed PhaseWrap score alone does not solve the value-readout packet;
- evidence that PhaseWrap-plus-distance can match RoPE-like argmax value retrieval on this local packet;
- bootstrap intervals over held-out test rows.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next downstream experiment should integrate the PhaseWrap-plus-distance adapter into a stronger small decoder-only transformer with learned token embeddings and matched compute, then evaluate non-phase-cued retrieval or compact QA tasks across multiple seeds.
