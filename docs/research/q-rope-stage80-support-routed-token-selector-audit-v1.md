# QRoPE Stage 80 Support-Routed Token Selector Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 80 tests the immediate implication of Stage 79: if same-seed support-complete exposure recovers held-out phase-cued support labels, can that recovered support be routed into token selection to repair phase-cued retrieval?

This is a coupling diagnostic, not a matched decoder-only transformer benchmark. It preserves the fair RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap comparison frame while explicitly excluding metadata lookup, evaluation-time `reference_delta`, `target_pos`, and `target_delta` access.

Reviewer command:

```powershell
python scripts\run_stage80_support_routed_token_selector_audit.py
```

## Result

Default run: five seeds, six methods, `examples_per_length=6`, 80 epochs, no failed runs.

| Task | Best method | Test top-1 | Mean target probability |
| --- | --- | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | `1.000000` | `0.748539` |
| `phase_cued_retrieval` | `sinusoidal` | `1.000000` | `1.000000` |
| `exact_offset_passkey` | `sinusoidal` | `0.650000` | `0.340343` |

Decision:

`SUPPORT_ROUTED_TOKEN_SELECTOR_SOLVES_PHASE_CUED_NOT_PROMOTION`

Mean phase-cued support accuracy: `1.000000`.

The phase-cued lane is solved by every tested method, including `no_position`, once recovered support is routed to the farthest in-context token congruent with the predicted phase class.

## Interpretation

Stage 80 is positive evidence that Stage 79's remaining failure was a coupling failure: recovered support was not being used correctly for token selection in the compact auxiliary copy-head path.

It is also negative evidence for positional-method promotion. The repair is method-nonspecific; `no_position`, `sinusoidal`, `alibi`, `rope_relative`, `phasewrap_bias`, and `phasewrap_adapter` all reach phase-cued top-1 `1.000000` under the support-routed selector.

The strongest honest claim remains bounded. Stage 80 proves the row family can be solved when a learned support signal is explicitly routed into the right token-selection rule. It does not prove that PhaseWrap-RoPE replaces RoPE, that a matched decoder-only transformer learns this routing, or that the repair is PhaseWrap-specific.

## Next Gate

The next useful gate is a learned matched decoder-only path that must infer the support-to-token routing from standard inputs and training loss, without a hard-coded farthest-congruent selector. The benchmark must keep the same failed-run retention and fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap reporting.
