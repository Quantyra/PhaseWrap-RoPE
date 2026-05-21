# PhaseWrap-RoPE Stage 46 Decoder Capacity Hardening Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 46 follows the Stage 45 matched decoder-only gate, which remained near chance. It asks a narrower diagnostic question: does longer training on the same one-block decoder-only harness establish enough train-set capacity to make positional-method comparisons meaningful?

The audit preserves the same fair method set:

- `rope_relative`
- `alibi`
- `sinusoidal`
- `no_position`
- `phasewrap_bias`
- `phasewrap_adapter`

It separates train, validation, and test metrics so capacity failure is not mistaken for positional-method evidence.

## Reviewer Command

```bash
python scripts/run_stage46_decoder_capacity_hardening_audit.py
```

This writes:

- `logs/automated_stage_gates/stage46_decoder_capacity_hardening_audit/manifest.json`
- `logs/automated_stage_gates/stage46_decoder_capacity_hardening_audit/results.json`
- `logs/automated_stage_gates/stage46_decoder_capacity_hardening_audit/summary.csv`
- `logs/automated_stage_gates/stage46_decoder_capacity_hardening_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage46_decoder_capacity_hardening_audit/failed_runs.json`

## Result

Stage 46 records `CAPACITY_NOT_ESTABLISHED`.

Longer training improves the tiny text-fact QA lane, but not enough to establish a reliable decoder-only promotion harness. The best train top-1 is `0.500000`, below the preregistered capacity threshold `0.750000`.

Best visible rows:

| Task | Method | Train top-1 | Train MRR | Test top-1 | Test MRR | Test target probability |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `phasewrap_adapter` | 0.500000 | 0.750000 | 0.500000 | 0.750000 | 0.008010 |
| `tiny_text_fact_qa` | `phasewrap_bias` | 0.500000 | 0.750000 | 0.500000 | 0.750000 | 0.008006 |
| `phase_cued_retrieval` | `alibi` | 0.250000 | 0.520833 | 0.000000 | 0.034369 | 0.007727 |
| `exact_offset_passkey` | `phasewrap_bias` | 0.250000 | 0.583333 | 0.000000 | 0.033258 | 0.007813 |
| `exact_offset_passkey` | `phasewrap_adapter` | 0.250000 | 0.583333 | 0.000000 | 0.033258 | 0.007813 |

The PhaseWrap-positive detail is preserved: `phasewrap_adapter` and `phasewrap_bias` are the strongest tiny text-fact QA rows by the audit ordering. However, target probabilities remain near uniform and the retrieval lanes do not generalize.

## Interpretation

Stage 46 strengthens the Stage 45 interpretation. The one-block decoder-only harness is not merely undertrained at 60 epochs; even a 300-epoch capacity audit does not fit the training rows well enough to promote positional-method conclusions. The honest claim remains bounded.

The next useful step is not to read Stage 46 as a PhaseWrap win. It is to replace or materially strengthen the decoder-only harness so it can first learn the task, then rerun the same fair RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap comparison.

## Claim Boundary

Supported:

- longer-training capacity audit for the matched one-block decoder-only harness;
- evidence that the one-block harness still lacks sufficient train-set capacity for promotion;
- weak PhaseWrap-positive tiny text-fact QA rows that should be preserved but not over-read;
- negative evidence that the current decoder-only path cannot yet adjudicate replacement claims.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that Stage 46 validates the one-block decoder as a positional-method discriminator.
