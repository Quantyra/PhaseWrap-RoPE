# PhaseWrap-RoPE Stage 87 In-Decoder Support-Routed Copy Expert Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 87 changes the decoder mechanism after Stage 86 showed the Stage 85 dual-auxiliary failure was not a short-budget artifact. It keeps the learned dual-auxiliary two-block pointer-generator decoder, but adds a structural in-decoder support-routed copy expert for phase-cued rows.

The expert uses the decoder's own learned support probabilities at evaluation. It does not receive gold support labels, `target_pos`, `target_delta`, or `reference_delta` at evaluation.

## Reviewer Command

```bash
python scripts/run_stage87_in_decoder_support_routed_copy_expert_audit.py
```

This writes:

- `logs/automated_stage_gates/stage87_in_decoder_support_routed_copy_expert_audit/manifest.json`
- `logs/automated_stage_gates/stage87_in_decoder_support_routed_copy_expert_audit/results.json`
- `logs/automated_stage_gates/stage87_in_decoder_support_routed_copy_expert_audit/summary.csv`
- `logs/automated_stage_gates/stage87_in_decoder_support_routed_copy_expert_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage87_in_decoder_support_routed_copy_expert_audit/failed_runs.json`

## Result

Stage 87 records `IN_DECODER_SUPPORT_ROUTED_COPY_EXPERT_SOLVES_PHASE_CUED_NOT_PROMOTION`.

Default run summary:

| task | best method | train top-1 | test top-1 | mean target probability |
| --- | --- | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | `1.000000` | `0.933334` | `0.109442` |
| `phase_cued_retrieval` | `rope_relative` | `0.900000` | `0.783333` | `0.222695` |
| `exact_offset_passkey` | `sinusoidal` | `0.966667` | `0.416667` | `0.058441` |

Additional decision fields:

- `generalization_top1_threshold`: `0.5`
- `retrieval_solved_tasks`: `["phase_cued_retrieval"]`
- `no_position_solved_retrieval_tasks`: `["phase_cued_retrieval"]`
- `phase_cued_best_support_accuracy`: `0.900000`
- `failed_runs`: `[]`

## Interpretation

Stage 87 shows that the learned support signal can drive held-out phase-cued token selection when the decoder is given a structural support-to-token copy expert. This repairs phase-cued retrieval for multiple methods, including `no_position`.

That is useful mechanism evidence, but it is not RoPE replacement evidence. The repair depends on an explicit routing expert, exact-offset remains below the retrieval threshold at top-1 `0.416667`, and `no_position` also solves the repaired phase-cued lane.

## Claim Boundary

Supported:

- a no-credential support-complete two-block pointer-generator audit with an in-decoder support-routed copy expert;
- evidence that the Stage 85 decoder's learned support probabilities can drive held-out token selection when a structural routing expert is provided;
- fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that a structural support-routed copy expert is standard free decoder-only language modeling;
- a claim that support-routed expert success is positional-method promotion evidence when no-position also solves;
- broad quantum advantage.

## Next Gate

The next useful gate should ask whether a less hand-specified decoder mechanism can learn the same support-to-token binding without a structural farthest-congruent copy expert, and whether exact-offset can be repaired at the same time.
