# PhaseWrap-RoPE Stage 88 Structural Retrieval-Routed Copy Expert Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 88 composes the two strongest structural retrieval repairs from prior gates:

- Stage 87's in-decoder support-routed copy expert for `phase_cued_retrieval`;
- Stage 71's positional-bias argmax copy expert for `exact_offset_passkey`.

The audit keeps the Stage 85 dual-auxiliary two-block pointer-generator backbone and evaluates the same RoPE/ALiBI/sinusoidal/no-position/PhaseWrap method set. The phase-cued route uses learned support probabilities at evaluation, not gold support labels, `target_pos`, `target_delta`, or `reference_delta`. The exact-offset route copies the argmax prefix token under each method's own positional-bias score.

## Reviewer Command

```bash
python scripts/run_stage88_structural_retrieval_routed_copy_expert_audit.py
```

This writes:

- `logs/automated_stage_gates/stage88_structural_retrieval_routed_copy_expert_audit/manifest.json`
- `logs/automated_stage_gates/stage88_structural_retrieval_routed_copy_expert_audit/results.json`
- `logs/automated_stage_gates/stage88_structural_retrieval_routed_copy_expert_audit/summary.csv`
- `logs/automated_stage_gates/stage88_structural_retrieval_routed_copy_expert_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage88_structural_retrieval_routed_copy_expert_audit/failed_runs.json`

## Result

Stage 88 records `STRUCTURAL_RETRIEVAL_ROUTED_COPY_EXPERT_SOLVES_RETRIEVAL_NOT_PROMOTION`.

Default run summary:

| task | best method | train top-1 | test top-1 | mean target probability |
| --- | --- | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | `1.000000` | `0.933334` | `0.109442` |
| `phase_cued_retrieval` | `rope_relative` | `0.900000` | `0.783333` | `0.222695` |
| `exact_offset_passkey` | `rope_relative` | `1.000000` | `1.000000` | `1.000000` |

Additional decision fields:

- `generalization_top1_threshold`: `0.5`
- `retrieval_solved_tasks`: `["phase_cued_retrieval", "exact_offset_passkey"]`
- `no_position_solved_retrieval_tasks`: `["phase_cued_retrieval"]`
- `phase_cued_best_support_accuracy`: `0.900000`
- `failed_runs`: `[]`

## Interpretation

Stage 88 shows that the original retrieval row family is jointly solvable when the decoder is given structural retrieval-routed copy experts. This is useful mechanism evidence because it separates row solvability from the earlier learned free-decoder failure.

It is not PhaseWrap-RoPE promotion evidence. The composed repair is structural, `rope_relative` leads both retrieval lanes in the default run, and `no_position` also crosses the phase-cued threshold.

## Claim Boundary

Supported:

- a no-credential support-complete two-block pointer-generator audit with structural retrieval-routed copy experts;
- evidence that structural support routing plus positional-bias copy can jointly solve original held-out retrieval;
- fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that structural retrieval-routed copy experts are standard free decoder-only language modeling;
- a claim that structural expert success is positional-method promotion evidence;
- broad quantum advantage.

## Next Gate

The next useful gate should remove structural copy routing and ask whether a learned matched decoder-only mechanism can discover the same phase-cued and exact-offset support-to-token bindings under fair method comparisons.
