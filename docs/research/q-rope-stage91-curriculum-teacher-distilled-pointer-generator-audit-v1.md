# PhaseWrap-RoPE Stage 91 Curriculum Teacher-Distilled Pointer Generator Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 91 tests whether the Stage 90 free-retrieval failure can be repaired by adding the intermediate length-40 rows to training.

It keeps the three-block teacher-distilled pointer-generator from Stage 90, adds length-40 curriculum rows to the same-seed multitask training set, and evaluates only on the original held-out lengths 48 and 64. Evaluation remains free: no structural copy route, teacher distribution, support label, `target_pos`, `target_delta`, or `reference_delta` is available.

## Reviewer Command

```bash
python scripts/run_stage91_curriculum_teacher_distilled_pointer_generator_audit.py
```

This writes:

- `logs/automated_stage_gates/stage91_curriculum_teacher_distilled_pointer_generator_audit/manifest.json`
- `logs/automated_stage_gates/stage91_curriculum_teacher_distilled_pointer_generator_audit/results.json`
- `logs/automated_stage_gates/stage91_curriculum_teacher_distilled_pointer_generator_audit/summary.csv`
- `logs/automated_stage_gates/stage91_curriculum_teacher_distilled_pointer_generator_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage91_curriculum_teacher_distilled_pointer_generator_audit/failed_runs.json`

## Result

Stage 91 records `CURRICULUM_TEACHER_DISTILLED_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION`.

Default run summary:

| task | best method | train top-1 | test top-1 | mean target probability |
| --- | --- | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | `1.000000` | `0.950000` | `0.091689` |
| `phase_cued_retrieval` | `sinusoidal` | `0.688889` | `0.033333` | `0.029417` |
| `exact_offset_passkey` | `sinusoidal` | `0.977778` | `0.333333` | `0.058070` |

Additional decision fields:

- `generalization_top1_threshold`: `0.5`
- `generalized_original_retrieval_tasks`: `[]`
- `retrieval_attention_repaired_tasks`: `[]`
- `phase_cued_best_support_accuracy`: `0.716667`
- `failed_runs`: `[]`

## Interpretation

Stage 91 does not repair free held-out retrieval. The length-40 curriculum improves tiny-text QA but leaves both original retrieval lanes below threshold. Exact-offset falls relative to Stage 90, and phase-cued remains near chance.

This keeps the Stage 70 claim boundary bounded: structural retrieval routes solve the row family, but added depth, structural-teacher distillation, and intermediate-length curriculum do not make the current free learned decoder generalize original retrieval.

## Claim Boundary

Supported:

- a no-credential support-complete length-curriculum three-block pointer-generator audit with training-only structural teacher distillation;
- evidence that adding length-40 curriculum rows does not repair free held-out original retrieval under this training setup;
- fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that a length-curriculum toy pointer-generator is full transformer-scale validation;
- a claim that curriculum or training-time structural teachers are positional-method promotion evidence;
- broad quantum advantage.

## Next Gate

The next useful gate should change the support-to-token binding objective itself rather than only adding depth, teacher distillation, or intermediate lengths.
