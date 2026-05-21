# PhaseWrap-RoPE Stage 60 Support Fallback Strictness Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 60 tests whether the Stage 59 seed-local lookup result depends on fallback decoding for query residues absent from the seed-local train support map.

It compares two deterministic copy-readout policies:

- `fallback_mod16`: Stage 59 behavior, where unseen query residues fall back to `reference_delta mod 16`;
- `strict_known_only`: unseen query residues receive only the distance prior, not an exact-distance or phase-congruence cue.

This is not a matched decoder-only transformer. It is a strictness audit for the Stage 59 lookup/copy diagnostic.

## Reviewer Command

```bash
python scripts/run_stage60_support_fallback_strictness_audit.py
```

This writes:

- `logs/automated_stage_gates/stage60_support_fallback_strictness_audit/manifest.json`
- `logs/automated_stage_gates/stage60_support_fallback_strictness_audit/results.json`
- `logs/automated_stage_gates/stage60_support_fallback_strictness_audit/summary.csv`
- `logs/automated_stage_gates/stage60_support_fallback_strictness_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage60_support_fallback_strictness_audit/failed_runs.json`

## Result

Stage 60 records `FALLBACK_DEPENDENT_PHASE_CUED_RETRIEVAL_NOT_PROMOTION`.

| Policy | Task | Best method | Test top-1 | Test target probability |
| --- | --- | --- | ---: | ---: |
| `fallback_mod16` | `phase_cued_retrieval` | `phasewrap_bias` / `phasewrap_adapter` / `no_position` / `alibi` | 0.750000 | 0.394084 |
| `strict_known_only` | `phase_cued_retrieval` | `sinusoidal` | 0.200000 | 0.057033 |
| `fallback_mod16` | `exact_offset_passkey` | `rope_relative` | 0.800000 | 0.356896 |
| `strict_known_only` | `exact_offset_passkey` | `rope_relative` | 0.950000 | 0.277514 |
| both | `tiny_text_fact_qa` | `rope_relative` | 1.000000 | 1.000000 |

No runs failed.

## Interpretation

Stage 60 shows the Stage 59 phase-cued retrieval result is fallback-dependent. When unseen seed-local query residues are not allowed to receive the fallback `mod 16` cue, phase-cued retrieval falls below the generalization threshold.

This strengthens the honest claim boundary. The current lookup/copy diagnostics show useful cue visibility and fallback behavior, but they do not show that a matched decoder has learned the support-aware phase-cued rule from standard inputs. They also do not show a PhaseWrap-specific positional advantage because `no_position` participates in the fallback solution.

## Claim Boundary

Supported:

- evidence that Stage 59 phase-cued threshold crossing depends on fallback decoding;
- evidence that strict seed-local support does not solve held-out phase-cued retrieval;
- fair method reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants;
- failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that fallback decoding is a matched decoder-only transformer;
- a claim that strict seed-local support coverage solves held-out phase-cued retrieval;
- a claim that this deterministic copy diagnostic is positional-method promotion evidence.
