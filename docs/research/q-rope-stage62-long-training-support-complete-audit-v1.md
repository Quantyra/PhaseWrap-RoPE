# PhaseWrap-RoPE Stage 62 Long-Training Support-Complete Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 62 tests whether the Stage 61 learned two-block decoder failure is simply a short-training-budget issue.

It keeps the Stage 61 support-complete setup:

- all five default seeds have complete phase-cued support coverage;
- learned token embeddings;
- two q/k/v/o attention blocks;
- learned vocab softmax output;
- matched RoPE/ALiBI/sinusoidal/no-position/PhaseWrap method variants;
- no fixed copy output, no lookup output, and no fallback cue decoder.

The change is longer training: `80` epochs instead of Stage 61's `20`.

## Reviewer Command

```bash
python scripts/run_stage62_long_training_support_complete_audit.py
```

This writes:

- `logs/automated_stage_gates/stage62_long_training_support_complete_audit/manifest.json`
- `logs/automated_stage_gates/stage62_long_training_support_complete_audit/results.json`
- `logs/automated_stage_gates/stage62_long_training_support_complete_audit/summary.csv`
- `logs/automated_stage_gates/stage62_long_training_support_complete_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage62_long_training_support_complete_audit/failed_runs.json`

## Result

Stage 62 records `LONG_TRAINING_SUPPORT_COMPLETE_CAPACITY_NOT_ESTABLISHED`.

All five default seeds retain complete phase-cued held-out support coverage from train rows (`test_known_fraction = 1.0`). Longer training improves train fit but remains below the `0.75` capacity threshold.

| Task | Best method | Train top-1 | Test top-1 | Test target probability |
| --- | --- | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | 0.166667 | 0.166667 | 0.166605 |
| `phase_cued_retrieval` | `phasewrap_adapter` by train; `alibi` by test ranking | 0.533333 | 0.000000 | 0.003387 |
| `exact_offset_passkey` | `phasewrap_bias` / `phasewrap_adapter` by train; `sinusoidal` by test ranking | 0.483333 | 0.016667 | 0.009767 |

No runs failed.

## Interpretation

Stage 62 shows that a longer training budget improves the support-complete learned decoder, but it still does not establish capacity. The best train lane is phase-cued retrieval with `phasewrap_adapter` at `0.533333`, below the `0.75` threshold, and held-out retrieval remains effectively unrepaired.

This preserves a useful positive detail: PhaseWrap adapter training fit improves most on the phase-cued lane under longer training. It also preserves the failure mode: the learned decoder still cannot support positional-method promotion because it does not fit or generalize retrieval well enough.

## Claim Boundary

Supported:

- evidence that longer training improves support-complete two-block train fit;
- evidence that longer training alone still does not establish learned decoder capacity;
- fair reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants;
- failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that longer training alone solves learned retrieval generalization;
- a claim that Stage 62 is positional-method promotion evidence.
