# PhaseWrap-RoPE Stage 85 Dual-Auxiliary Pointer-Generator Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 85 tests the next support-to-token blocker after Stage 84. It keeps the support-complete same-seed multitask Stage 10 rows and the fair RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap comparison frame, but trains a two-block pointer-generator decoder with both:

- phase-cued support-class auxiliary supervision; and
- retrieval-row target-position attention auxiliary supervision.

The target and support labels are training-only diagnostics. Evaluation does not receive support labels, `target_pos`, `target_delta`, or `reference_delta`.

## Reviewer Command

```bash
python scripts/run_stage85_dual_auxiliary_pointer_generator_audit.py
```

This writes:

- `logs/automated_stage_gates/stage85_dual_auxiliary_pointer_generator_audit/manifest.json`
- `logs/automated_stage_gates/stage85_dual_auxiliary_pointer_generator_audit/results.json`
- `logs/automated_stage_gates/stage85_dual_auxiliary_pointer_generator_audit/summary.csv`
- `logs/automated_stage_gates/stage85_dual_auxiliary_pointer_generator_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage85_dual_auxiliary_pointer_generator_audit/failed_runs.json`

## Result

Stage 85 records `DUAL_AUXILIARY_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION`.

Default run summary:

| task | best method | train top-1 | test top-1 | mean target probability |
| --- | --- | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | `1.000000` | `0.933334` | `0.109442` |
| `phase_cued_retrieval` | `sinusoidal` | `0.883333` | `0.050000` | `0.029205` |
| `exact_offset_passkey` | `sinusoidal` | `0.966667` | `0.416667` | `0.058441` |

Additional decision fields:

- `generalization_top1_threshold`: `0.5`
- `phase_cued_best_support_accuracy`: `0.900000`
- `retrieval_attention_repaired_tasks`: `[]`
- `generalized_original_retrieval_tasks`: `[]`
- `failed_runs`: `[]`

## Interpretation

Dual support and target-attention supervision improves some train capacity and gives a stronger diagnostic than Stage 84, but it still does not cross the held-out retrieval threshold. The best exact-offset result reaches top-1 `0.416667`, below the `0.5` generalization gate, and phase-cued retrieval remains near chance at top-1 `0.050000`.

This narrows the current blocker: the failure is not only missing support labels or missing target-attention training signal. The current learned decoder path still does not convert training-time support/target supervision into held-out support-to-token retrieval.

## Claim Boundary

Supported:

- a no-credential support-complete two-block pointer-generator audit with support and target-attention auxiliary losses;
- evidence about whether training-only support and target-position supervision repairs held-out support-to-token routing;
- fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that target-position supervision is standard free decoder-only language modeling;
- a claim that dual-auxiliary diagnostics are positional-method promotion evidence by themselves;
- broad quantum advantage.

## Next Gate

The next gate should avoid adding more compact auxiliary heads unless it materially changes the decoder mechanism. A useful next step would test a stronger matched decoder-only architecture or curriculum that can preserve held-out support-to-token routing without evaluation-time metadata.
