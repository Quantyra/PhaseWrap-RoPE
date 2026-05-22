# PhaseWrap-RoPE Stage 92 Support-Binding Teacher Pointer Generator Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 92 tests whether a more direct support-to-token binding objective repairs the free learned decoder path.

It keeps the Stage 91 length-curriculum three-block pointer-generator, adds a training-only support-weighted copied-token binding loss for phase-cued rows, and still evaluates only the free learned pointer-generator distribution. Evaluation does not receive structural copy routes, teacher distributions, support labels, `target_pos`, `target_delta`, or `reference_delta`.

## Reviewer Command

```bash
python scripts/run_stage92_support_binding_teacher_pointer_generator_audit.py
```

This writes:

- `logs/automated_stage_gates/stage92_support_binding_teacher_pointer_generator_audit/manifest.json`
- `logs/automated_stage_gates/stage92_support_binding_teacher_pointer_generator_audit/results.json`
- `logs/automated_stage_gates/stage92_support_binding_teacher_pointer_generator_audit/summary.csv`
- `logs/automated_stage_gates/stage92_support_binding_teacher_pointer_generator_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage92_support_binding_teacher_pointer_generator_audit/failed_runs.json`

## Result

Stage 92 records `SUPPORT_BINDING_TEACHER_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION`.

Default run summary:

| task | best method | train top-1 | test top-1 | mean target probability |
| --- | --- | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | `0.977778` | `0.883333` | `0.082920` |
| `phase_cued_retrieval` | `alibi` | `0.088889` | `0.050000` | `0.020765` |
| `exact_offset_passkey` | `sinusoidal` | `0.988889` | `0.366667` | `0.059161` |

Additional decision fields:

- `generalization_top1_threshold`: `0.5`
- `generalized_original_retrieval_tasks`: `[]`
- `retrieval_attention_repaired_tasks`: `[]`
- `phase_cued_best_support_accuracy`: `0.850000`
- `failed_runs`: `[]`

## Interpretation

Stage 92 does not repair free held-out retrieval. A direct support-weighted copied-token binding loss for phase-cued rows still fails to transfer the structural route into the learned pointer-generator output distribution.

This keeps the Stage 70 claim boundary bounded: support signals can be learned and structural routes can solve the row family, but current learned free decoders do not internalize the original support-to-token binding under fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons.

## Claim Boundary

Supported:

- a no-credential support-complete length-curriculum three-block pointer-generator audit with direct support-to-token binding supervision;
- evidence that direct support-binding supervision does not repair free held-out original retrieval under this training setup;
- fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that support-binding supervision is full transformer-scale validation;
- a claim that training-time support-binding teachers are positional-method promotion evidence;
- broad quantum advantage.

## Next Gate

The next useful gate should either move to a more standard transformer implementation or close the current toy-decoder lane as bounded unless a materially different learned binding mechanism is introduced.
