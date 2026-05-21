# PhaseWrap-RoPE Stage 59 Seed-Local Query Support Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 59 tests whether the Stage 58 pooled support lookup survives a stricter per-seed train-only setting. Each seed gets its own visible query-token support map learned only from that seed's phase-cued train rows, then the same deterministic cue-copy readout is evaluated under the fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparison frame.

This is not a matched decoder-only transformer. It is a stricter lookup/copy diagnostic that removes cross-seed pooling.

## Reviewer Command

```bash
python scripts/run_stage59_seed_local_query_support_audit.py
```

This writes:

- `logs/automated_stage_gates/stage59_seed_local_query_support_audit/manifest.json`
- `logs/automated_stage_gates/stage59_seed_local_query_support_audit/results.json`
- `logs/automated_stage_gates/stage59_seed_local_query_support_audit/summary.csv`
- `logs/automated_stage_gates/stage59_seed_local_query_support_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage59_seed_local_query_support_audit/failed_runs.json`

## Result

Stage 59 records `SEED_LOCAL_QUERY_SUPPORT_PARTIAL_COVERAGE_SOLVES_NOT_PROMOTION`.

| Task | Best method | Test top-1 | Test target probability |
| --- | --- | ---: | ---: |
| `tiny_text_fact_qa` | `rope_relative` | 1.000000 | 1.000000 |
| `exact_offset_passkey` | `rope_relative` | 0.800000 | 0.356896 |
| `phase_cued_retrieval` | `phasewrap_bias` / `phasewrap_adapter` / `no_position` / `alibi` | 0.750000 | 0.394084 |

No runs failed. The seed-local phase-cued train maps have zero direct held-out test support coverage for the default split, so the threshold-crossing phase-cued result is not proof that the support map generalized. It reflects fallback cue decoding plus deterministic copy output, and `no_position` solves under the same path.

## Interpretation

Stage 59 narrows the Stage 58 claim. Cross-seed pooling was not required to cross the loose retrieval threshold, but per-seed train rows do not cover the held-out phase-cued support values in the default split. The result therefore remains a bounded diagnostic: useful for understanding cue/fallback behavior, not evidence that a matched decoder has internalized the support-aware rule.

It still does not support a PhaseWrap positional-method claim. The repair is a deterministic seed-local lookup plus fallback and copy output, not a matched learned decoder-only transformer, and `no_position` reaches the same phase-cued top-1 as the PhaseWrap variants.

## Claim Boundary

Supported:

- evidence that seed-local support coverage is incomplete on the default held-out phase-cued split;
- evidence that fallback cue decoding can still cross the loose retrieval threshold;
- fair method reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants;
- failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that a seed-local lookup map is a matched decoder-only transformer;
- a claim that this deterministic cue-copy diagnostic is positional-method promotion evidence.
