# PhaseWrap-RoPE Stage 89 Structural Teacher-Distilled Pointer Generator Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 89 asks whether the Stage 88 structural retrieval routes can be transferred into the learned decoder rather than used at evaluation.

It keeps the Stage 85 dual-auxiliary two-block pointer-generator backbone, but adds a training-only structural teacher loss on retrieval rows. At validation and test time, the model emits only the ordinary learned pointer-generator distribution. It does not receive structural copy routes, teacher distributions, support labels, `target_pos`, `target_delta`, or `reference_delta`.

## Reviewer Command

```bash
python scripts/run_stage89_structural_teacher_distilled_pointer_generator_audit.py
```

This writes:

- `logs/automated_stage_gates/stage89_structural_teacher_distilled_pointer_generator_audit/manifest.json`
- `logs/automated_stage_gates/stage89_structural_teacher_distilled_pointer_generator_audit/results.json`
- `logs/automated_stage_gates/stage89_structural_teacher_distilled_pointer_generator_audit/summary.csv`
- `logs/automated_stage_gates/stage89_structural_teacher_distilled_pointer_generator_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage89_structural_teacher_distilled_pointer_generator_audit/failed_runs.json`

## Result

Stage 89 records `STRUCTURAL_TEACHER_DISTILLED_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION`.

Default run summary:

| task | best method | train top-1 | test top-1 | mean target probability |
| --- | --- | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | `0.950000` | `0.866667` | `0.095037` |
| `phase_cued_retrieval` | `sinusoidal` | `0.900000` | `0.050000` | `0.029135` |
| `exact_offset_passkey` | `sinusoidal` | `0.950000` | `0.366667` | `0.056805` |

Additional decision fields:

- `generalization_top1_threshold`: `0.5`
- `generalized_original_retrieval_tasks`: `[]`
- `retrieval_attention_repaired_tasks`: `[]`
- `phase_cued_best_support_accuracy`: `0.900000`
- `failed_runs`: `[]`

## Interpretation

Stage 89 is a negative transfer result. Training-time structural teacher distillation preserves capacity and retains a strong learned support signal, but the free learned pointer-generator still does not generalize held-out retrieval.

This strengthens the Stage 70 bounded-claim posture: structural retrieval solvability is real, but the current learned decoder path has not internalized the support-to-token binding under fair held-out RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons.

## Claim Boundary

Supported:

- a no-credential support-complete two-block pointer-generator audit with training-only structural teacher distillation;
- evidence that Stage 88 structural retrieval routes do not transfer into free held-out token retrieval under this decoder/training budget;
- fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that training-time structural teachers are standard free decoder-only language modeling;
- a claim that structural teacher distillation is positional-method promotion evidence;
- broad quantum advantage.

## Next Gate

The next useful gate should change the learned architecture or row curriculum enough to test whether the support-to-token binding can be learned without structural evaluation routes, while preserving the same fair method comparison and failure reporting.
