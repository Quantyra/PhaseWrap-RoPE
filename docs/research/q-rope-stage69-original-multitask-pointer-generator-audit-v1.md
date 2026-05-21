# PhaseWrap-RoPE Stage 69 Original Multitask Pointer-Generator Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 69 tests whether the Stage 64-68 retrieval failure is partly caused by training each original Stage 10 task in isolation.

For each seed and method, the audit trains one Stage 64 two-block learned pointer-generator on all same-seed original Stage 10 train rows:

- `phase_cued_retrieval`
- `exact_offset_passkey`
- `tiny_text_fact_qa`

It then evaluates each original task separately on unchanged validation and held-out test rows. No content-key auxiliary rows, row metadata, support lookup, or fallback cue help are added.

## Reviewer Command

```bash
python scripts/run_stage69_original_multitask_pointer_generator_audit.py
```

This writes:

- `logs/automated_stage_gates/stage69_original_multitask_pointer_generator_audit/manifest.json`
- `logs/automated_stage_gates/stage69_original_multitask_pointer_generator_audit/results.json`
- `logs/automated_stage_gates/stage69_original_multitask_pointer_generator_audit/summary.csv`
- `logs/automated_stage_gates/stage69_original_multitask_pointer_generator_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage69_original_multitask_pointer_generator_audit/failed_runs.json`

## Result

Stage 69 records `ORIGINAL_MULTITASK_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION`.

| Task | Best train method | Best train top-1 | Best test method | Best test top-1 |
| --- | --- | ---: | --- | ---: |
| `phase_cued_retrieval` | `sinusoidal` | 0.983333 | `no_position` | 0.016667 |
| `exact_offset_passkey` | `sinusoidal` | 1.000000 | `sinusoidal` | 0.033333 |
| `tiny_text_fact_qa` | `sinusoidal` | 1.000000 | `sinusoidal` | 0.516667 |

No runs failed.

## Interpretation

Stage 69 is negative evidence for simple original-task multitask training as the missing mechanism.

The result preserves capacity and the tiny text-fact QA positive, but original held-out retrieval remains far below the `0.500000` generalization threshold. Shared training across the original Stage 10 tasks is therefore not enough to repair the phase-cued/exact-offset retrieval blocker.

This keeps the current claim boundary unchanged: PhaseWrap-RoPE has useful compact and diagnostic evidence, but no fair matched decoder result yet supports a RoPE-replacement or positional-method promotion claim.

## Claim Boundary

Supported:

- evidence that original-row multitask training preserves capacity in the two-block pointer-generator path;
- evidence that original-row multitask training does not repair held-out retrieval generalization;
- fair reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants;
- failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that original multitask training is equivalent to a larger decoder-only language model;
- a claim that Stage 69 is positional-method promotion evidence.
