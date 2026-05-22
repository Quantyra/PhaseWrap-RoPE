# QRoPE Stage 82 Learned Support-Routing Head Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 82 tests the remaining hard-coded part of Stage 81. Stage 81 routed learned support probabilities through a fixed farthest-congruent token selector. Stage 82 replaces that hard selector with a learned three-scale routing head over prefix positions.

The routing head can use method positional bias, learned support-congruence scores, and normalized distance. It is trained from token-copy loss and does not receive evaluation-time `reference_delta`, `target_pos`, or `target_delta`.

Reviewer command:

```powershell
python scripts\run_stage82_learned_support_routing_head_audit.py
```

## Result

Default run: five seeds, six methods, `examples_per_length=6`, 80 support-head epochs, 120 routing-head epochs, no failed runs.

| Task | Best method | Test top-1 | Mean target probability |
| --- | --- | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | `1.000000` | `0.748539` |
| `phase_cued_retrieval` | `sinusoidal` | `0.333333` | `0.275733` |
| `exact_offset_passkey` | `sinusoidal` | `0.650000` | `0.340343` |

Decision:

`LEARNED_SUPPORT_ROUTING_HEAD_SUPPORT_RECOVERED_RETRIEVAL_FAILED`

Mean phase-cued support accuracy: `1.000000`.

## Interpretation

Stage 82 preserves support recovery but fails to preserve the Stage 80/81 phase-cued repair once the farthest-congruent routing rule must be learned by a compact routing head.

This sharpens the current blocker. The issue is no longer support-label recovery, and it is not solved merely by soft support probabilities. The remaining blocker is learning the support-to-token routing rule from standard training signals.

The strongest honest claim remains bounded. Stage 82 does not support PhaseWrap-RoPE as a RoPE replacement, does not validate a matched decoder-only transformer, and does not support positional-method promotion.

## Next Gate

The next useful gate is a stronger learned decoder path with enough capacity and supervision structure to learn the farthest-congruent support-to-token routing rule under the same fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparison.
