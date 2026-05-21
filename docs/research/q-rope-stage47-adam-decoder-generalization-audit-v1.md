# PhaseWrap-RoPE Stage 47 Adam Decoder Generalization Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 47 tests whether the Stage 45-46 one-block decoder-only harness failed because of optimizer weakness. It keeps the same model family, tasks, train-short/test-long splits, and fair positional-method comparison set, but replaces plain full-batch gradient descent with full-batch Adam.

The fair method set remains:

- `rope_relative`
- `alibi`
- `sinusoidal`
- `no_position`
- `phasewrap_bias`
- `phasewrap_adapter`

## Reviewer Command

```bash
python scripts/run_stage47_adam_decoder_generalization_audit.py
```

This writes:

- `logs/automated_stage_gates/stage47_adam_decoder_generalization_audit/manifest.json`
- `logs/automated_stage_gates/stage47_adam_decoder_generalization_audit/results.json`
- `logs/automated_stage_gates/stage47_adam_decoder_generalization_audit/summary.csv`
- `logs/automated_stage_gates/stage47_adam_decoder_generalization_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage47_adam_decoder_generalization_audit/failed_runs.json`

## Result

Stage 47 records `TRAIN_FIT_WITH_PARTIAL_GENERALIZATION`.

Adam fixes the train-fit failure from Stage 46: every reported method reaches train top-1 `1.000000` on the audited rows. The generalization result is split:

| Task | Best visible method | Train top-1 | Validation top-1 | Test top-1 | Test MRR | Test target probability |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `phasewrap_bias` | 1.000000 | 0.500000 | 0.750000 | 0.875000 | 0.744825 |
| `tiny_text_fact_qa` | `phasewrap_adapter` | 1.000000 | 0.500000 | 0.750000 | 0.875000 | 0.741790 |
| `tiny_text_fact_qa` | `rope_relative` | 1.000000 | 0.500000 | 0.750000 | 0.875000 | 0.740103 |
| `phase_cued_retrieval` | `phasewrap_bias` | 1.000000 | 0.000000 | 0.000000 | 0.030804 | 0.000050 |
| `exact_offset_passkey` | `rope_relative` | 1.000000 | 0.000000 | 0.000000 | 0.038734 | 0.000001 |

The strongest positive is real but narrow: PhaseWrap variants lead the tiny text-fact QA lane by target probability and tie top-1/MRR. The failure mode is also clear: both retrieval lanes still fail validation/test generalization despite perfect train fit.

## Interpretation

Stage 47 is stronger evidence than Stage 46 because it separates train capacity from held-out generalization. The one-block decoder can now memorize or fit the audited train rows, so Stage 46's capacity failure was partly optimizer-driven. However, the fair positional comparison still cannot support promotion because the retrieval tasks do not generalize.

The honest claim remains bounded:

- PhaseWrap has a weak positive in the tiny text-fact QA lane under Adam.
- RoPE-like scoring is not displaced on the retrieval lanes because the retrieval lanes fail for every method.
- Train fit alone is not promotion evidence.

## Claim Boundary

Supported:

- optimizer-hardening evidence for the one-block decoder-only harness;
- evidence that Adam establishes train fit on the audited rows;
- a narrow PhaseWrap-positive tiny text-fact QA result;
- negative evidence that phase-cued retrieval and exact-offset passkey still fail held-out generalization.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that tiny text-fact QA alone is enough for promotion.
