# QRoPE Stage 84 Support-Auxiliary Pointer-Generator Audit v1

Date: `2026-05-22`

Status: `completed`

## Purpose

Stage 84 tests whether the remaining Stage 83 support-to-token routing blocker is repaired by moving support supervision inside a stronger decoder-style path. It trains the two-block pointer-generator decoder on support-complete same-seed multitask rows and adds an auxiliary support-class classifier from the decoder query state.

The support auxiliary loss is applied to phase-cued train rows only. Evaluation does not receive support labels, `target_pos`, or `target_delta`.

Reviewer command:

```powershell
python scripts\run_stage84_support_auxiliary_pointer_generator_audit.py
```

## Result

Default run: five seeds, six methods, `examples_per_length=6`, 80 epochs, support auxiliary weight `0.7`, no failed runs.

| Task | Best method | Train top-1 | Test top-1 | Mean target probability |
| --- | --- | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | `1.000000` | `0.583333` | `0.480035` |
| `phase_cued_retrieval` | `sinusoidal` | `1.000000` | `0.016667` | `0.018978` |
| `exact_offset_passkey` | `sinusoidal` | `1.000000` | `0.033333` | `0.020241` |

Decision:

`SUPPORT_AUXILIARY_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION`

Best phase-cued test support accuracy: `0.716667`.

## Interpretation

Stage 84 establishes train capacity but does not repair held-out retrieval generalization. In-decoder support supervision improves the diagnostic strength versus standalone routing heads, but the decoder still does not learn the held-out support-to-token routing rule.

The strongest honest claim remains bounded. Stage 84 does not support PhaseWrap-RoPE as a RoPE replacement, does not validate a production language model, and does not support positional-method promotion.

## Next Gate

The next useful gate should change the learned decoder mechanism or data regime enough to address held-out support-to-token generalization directly, while preserving the same fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparison and failed-run reporting.
