# PhaseWrap-RoPE Stage 15 Learned Attention-Readout Benchmark v1

Date: `2026-05-20`

## Purpose

Stage 15 adds a compact learned attention-readout benchmark over the Stage 14 key-value rows. Instead of using a linear positional adapter, each method trains a one-hidden-layer scorer over its positional features and then evaluates target value-token retrieval on held-out length-1024 rows.

This is still a local learned attention probe. It is not a full decoder-only transformer benchmark and not proof that PhaseWrap-RoPE replaces RoPE.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage15_learned_attention/manifest.json`
- Results: `logs/automated_stage_gates/stage15_learned_attention/results.json`
- Summary CSV: `logs/automated_stage_gates/stage15_learned_attention/summary.csv`
- Task summary CSV: `logs/automated_stage_gates/stage15_learned_attention/task_summary.csv`
- Runner: `scripts/run_stage15_learned_attention.py`
- Implementation: `src/qrope/stage15_learned_attention.py`
- Tests: `tests/test_stage15_learned_attention.py`

## Reproduce

```bash
python scripts/run_stage15_learned_attention.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Task

Stage 15 reuses the Stage 14 key-value attention-readout rows. Targets remain explicit retrieval-rule value tokens, not PhaseWrap-selected positions. The model trains on context lengths `128` and `256`, declares length `512` as validation, and evaluates on length `1024`.

Each method trains a one-hidden-layer scorer over its positional feature family:

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
| `phasewrap_distance_adapter` | 60 | 1.000000 | 1.000000-1.000000 | 1.000000 | 1.000000-1.000000 | 0.516181 | 1.000000 |
| `rope_relative` | 60 | 0.933333 | 0.850000-0.983333 | 0.966667 | 0.933333-0.991667 | 0.678210 | 1.066667 |
| `sinusoidal` | 60 | 0.733333 | 0.616667-0.833333 | 0.859722 | 0.802778-0.913889 | 0.476457 | 1.316667 |
| `phasewrap_residual_adapter` | 60 | 0.500000 | 0.383333-0.616667 | 0.718056 | 0.640278-0.800000 | 0.338508 | 1.716667 |
| `alibi` | 60 | 0.100000 | 0.016667-0.166667 | 0.214748 | 0.153077-0.289779 | 0.042730 | 12.216667 |
| `no_position` | 60 | 0.083333 | 0.016667-0.166667 | 0.195125 | 0.127224-0.268153 | 0.042635 | 14.466667 |
| `phasewrap_score` | 60 | 0.050000 | 0.000000-0.100000 | 0.147274 | 0.091964-0.217219 | 0.050945 | 14.300000 |

The learned scorer improves the PhaseWrap-plus-distance mechanism enough to lead on argmax retrieval for this local held-out packet. RoPE-like scoring still assigns higher target value probability, so the result is mixed: PhaseWrap-plus-distance is promising for ranking, while RoPE remains stronger on calibration/probability mass.

## Claim Boundary

Supported:

- deterministic train-short/test-long learned attention-readout comparison on non-phase-cued key-value rows;
- evidence that fixed PhaseWrap score alone remains weak;
- evidence that a learned scorer over PhaseWrap-plus-distance features can lead argmax value retrieval on this local packet;
- bootstrap intervals over held-out test rows.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next downstream experiment should move from this learned attention-readout probe to a stronger small decoder-only transformer with learned token embeddings, matched compute, multiple seeds, failed-run artifacts, and non-phase-cued retrieval or compact QA tasks.
