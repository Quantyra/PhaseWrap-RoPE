# QRoPE Stage 83 Nonlinear Support-Routing Bridge Audit v1

Date: `2026-05-22`

Status: `completed`

## Purpose

Stage 83 tests whether Stage 82's compact scalar-router failure is mainly a routing-capacity problem. Stage 81 routed learned support probabilities through a fixed farthest-congruent token selector. Stage 82 replaced that selector with three learned routing scales and failed to preserve the repair. Stage 83 replaces the scalar router with a nonlinear per-position routing bridge.

The routing bridge can use method positional bias, learned support-congruence scores, normalized distance, and pairwise/quadratic interaction features. It is trained from token-copy loss and does not receive evaluation-time `reference_delta`, `target_pos`, or `target_delta`.

Reviewer command:

```powershell
python scripts\run_stage83_nonlinear_support_routing_bridge_audit.py
```

## Result

Default run: five seeds, six methods, `examples_per_length=6`, 80 support-head epochs, 160 nonlinear routing-bridge epochs, hidden width 8, no failed runs.

| Task | Best method | Test top-1 | Mean target probability |
| --- | --- | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | `1.000000` | `0.748539` |
| `phase_cued_retrieval` | `phasewrap_adapter` | `0.283333` | `0.441248` |
| `exact_offset_passkey` | `sinusoidal` | `0.650000` | `0.340343` |

Decision:

`NONLINEAR_SUPPORT_ROUTING_BRIDGE_SUPPORT_RECOVERED_RETRIEVAL_FAILED`

Mean phase-cued support accuracy: `1.000000`.

## Interpretation

Stage 83 preserves support recovery and raises phase-cued target probability versus Stage 82, but it still fails to preserve the Stage 80/81 phase-cued repair once the farthest-congruent routing rule must be learned rather than hard-coded.

This sharpens the current blocker. The issue is no longer support-label recovery, and it is not solved merely by soft support probabilities or a small nonlinear per-position bridge. The remaining blocker is learning the support-to-token routing rule from standard training signals in a stronger matched decoder path.

The strongest honest claim remains bounded. Stage 83 does not support PhaseWrap-RoPE as a RoPE replacement, does not validate a matched decoder-only transformer, and does not support positional-method promotion.

## Next Gate

The next useful gate is a stronger matched decoder path with enough capacity and supervision structure to learn support-to-token routing under the same fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparison.
