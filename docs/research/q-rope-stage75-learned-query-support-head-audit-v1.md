# PhaseWrap-RoPE Stage 75 Learned Query Support Head Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 75 tests whether the Stage 74 leave-one-seed query-support lookup can be replaced by a learned visible-cue support head.

For each held-out seed, the audit trains a small softmax classifier from visible query-token features to phase-cued support classes using only the other seeds' train rows. It then evaluates the same copy-readout family across RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap variants.

This is stronger than the Stage 74 hard lookup, but it is still not a full matched decoder-only transformer. It is a learned query-support-head diagnostic with deterministic copy readout.

## Reviewer Command

```bash
python scripts/run_stage75_learned_query_support_head_audit.py
```

This writes:

- `logs/automated_stage_gates/stage75_learned_query_support_head_audit/manifest.json`
- `logs/automated_stage_gates/stage75_learned_query_support_head_audit/results.json`
- `logs/automated_stage_gates/stage75_learned_query_support_head_audit/summary.csv`
- `logs/automated_stage_gates/stage75_learned_query_support_head_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage75_learned_query_support_head_audit/failed_runs.json`

## Result

Stage 75 records `LEARNED_QUERY_SUPPORT_HEAD_SOLVES_PHASE_CUED_NOT_PROMOTION`.

| Task | Best method | Test top-1 | Test target probability |
| --- | --- | ---: | ---: |
| `tiny_text_fact_qa` | `rope_relative` / `no_position` / `alibi` | 1.000000 | 1.000000 |
| `phase_cued_retrieval` | `phasewrap_bias` / `phasewrap_adapter` / `no_position` | 0.900000 | 0.461168 |
| `exact_offset_passkey` | `rope_relative` | 0.600000 | 0.279211 |

Mean held-out phase-cued support-head accuracy is `1.000000`. No runs failed.

## Interpretation

Stage 75 is a real improvement over Stage 74's deterministic support lookup: the visible query cue can be learned by a small support classifier under leave-one-seed evaluation.

The result still does not promote PhaseWrap-RoPE as a positional method. `no_position` reaches the same `0.900000` phase-cued top-1 as the PhaseWrap variants, and the learned component is a standalone support head feeding a deterministic copy readout rather than a matched decoder-only transformer.

The honest positive claim is narrower: the original phase-cued row family contains a visible cue that a learned support head can internalize across seeds. The next promotion-relevant step is to integrate that recovery into a matched decoder-only model and preserve the same fair baselines.

## Claim Boundary

Supported:

- evidence that learned leave-one-seed visible query-support recovery solves phase-cued retrieval;
- evidence that the support-head recovery generalizes across seeds in this synthetic row family;
- fair reporting across RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap variants.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that a standalone query-support head is a matched decoder-only transformer;
- a claim that learned visible-cue recovery is positional-method promotion evidence when `no_position` solves too.

## Next Gate

The next gate should integrate visible-cue recovery into a matched learned decoder-only mechanism rather than a separate support head, then rerun the same fair RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap comparison.
