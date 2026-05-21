# PhaseWrap-RoPE Stage 77 Auxiliary Support Copy Head Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 77 tests whether the Stage 76 integrated support/copy failure can be repaired by adding explicit support-classification supervision to the same compact copy-head objective.

For each seed and method, the audit trains one same-seed support/copy head on the original Stage 10 train rows. The loss combines token-copy loss with an auxiliary phase-cued support loss. It then evaluates train, validation, and held-out test rows across RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap variants.

This is stronger than Stage 76 as an integrated-objective diagnostic, but it is still not a full matched decoder-only transformer.

## Reviewer Command

```bash
python scripts/run_stage77_auxiliary_support_copy_head_audit.py
```

This writes:

- `logs/automated_stage_gates/stage77_auxiliary_support_copy_head_audit/manifest.json`
- `logs/automated_stage_gates/stage77_auxiliary_support_copy_head_audit/results.json`
- `logs/automated_stage_gates/stage77_auxiliary_support_copy_head_audit/summary.csv`
- `logs/automated_stage_gates/stage77_auxiliary_support_copy_head_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage77_auxiliary_support_copy_head_audit/failed_runs.json`

## Result

Stage 77 records `AUXILIARY_SUPPORT_COPY_HEAD_PARTIAL_RETRIEVAL`.

| Task | Best method | Test top-1 | Test target probability |
| --- | --- | ---: | ---: |
| `tiny_text_fact_qa` | `rope_relative` | 1.000000 | 0.752589 |
| `phase_cued_retrieval` | `sinusoidal` | 0.000000 | 0.034495 |
| `exact_offset_passkey` | `rope_relative` | 0.600000 | 0.257033 |

Mean held-out phase-cued support accuracy is `0.000000`. No runs failed.

## Interpretation

Stage 77 is another negative integration result. Auxiliary support supervision does not preserve the Stage 75 phase-cued repair when the model is trained same-seed and evaluated on held-out phase-cued rows.

The exact-offset lane remains partially repaired for `rope_relative`, but phase-cued retrieval remains zero for every tested method. This means the current integrated support/copy path still does not generalize the visible support cue to held-out phase-cued rows.

## Claim Boundary

Supported:

- evidence that auxiliary support supervision does not repair the integrated phase-cued failure;
- evidence that exact-offset remains partially repaired for `rope_relative`;
- fair reporting across RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap variants.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that this compact auxiliary copy-head is a matched decoder-only transformer;
- a claim that Stage 77 supports positional-method promotion.

## Next Gate

The next gate should either change the data exposure/generalization setup enough to explain why same-seed support supervision fails held-out phase-cued support, or move to a genuinely matched decoder-only architecture that can preserve visible-cue recovery on held-out rows.
