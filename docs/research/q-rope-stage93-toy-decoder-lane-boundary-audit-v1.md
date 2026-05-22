# PhaseWrap-RoPE Stage 93 Toy Decoder Lane Boundary Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 93 formalizes the current toy decoder lane boundary instead of adding another small pointer-generator variant.

It reads existing structural and free learned audit manifests, separates structural copy-route evidence from free learned pointer-generator evidence, and records whether the current lane supports any positional-method promotion claim.

## Reviewer Command

```bash
python scripts/run_stage93_toy_decoder_lane_boundary_audit.py
```

This writes:

- `logs/automated_stage_gates/stage93_toy_decoder_lane_boundary_audit/manifest.json`
- `logs/automated_stage_gates/stage93_toy_decoder_lane_boundary_audit/results.json`
- `logs/automated_stage_gates/stage93_toy_decoder_lane_boundary_audit/summary.csv`

## Result

Stage 93 records `TOY_DECODER_LANE_BOUND_FREE_RETRIEVAL_UNSOLVED`.

Default run summary:

| lane | evidence | result |
| --- | --- | --- |
| structural copy route | Stage 88 jointly solves `phase_cued_retrieval` and `exact_offset_passkey` | row family is structurally solvable |
| free learned pointer-generator | Stages 64/65/68/69/84/85/86/89/90/91/92 | no full free held-out original retrieval solve |
| positional-method promotion | free learned full solve with PhaseWrap-led methods | not supported |

Best free learned held-out top-1 by original retrieval task:

| task | stage | method | top-1 |
| --- | --- | --- | ---: |
| `phase_cued_retrieval` | `stage85_dual_auxiliary_pointer_generator_audit` | `sinusoidal` | `0.050000` |
| `exact_offset_passkey` | `stage90_three_block_teacher_distilled_pointer_generator_audit` | `sinusoidal` | `0.433333` |

## Interpretation

The current toy pointer-generator lane is bounded as insufficient for the promotional claim. Structural copy experts can supply the support-to-token route, but the audited free learned decoders have not internalized it under fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons.

This is progress toward the strongest honest claim because it prevents small variant churn from being mistaken for improving evidence.

## Claim Boundary

Supported:

- a no-credential boundary audit over existing structural and free learned toy decoder evidence;
- evidence that structural copy routes can solve the original retrieval row family while free learned toy pointer-generators have not internalized the route;
- a next-gate recommendation for moving beyond small pointer-generator variants before any positional-method promotion claim.

Excluded:

- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that PhaseWrap-RoPE is currently better than RoPE in fair matched transformer settings;
- a claim that structural copy experts are standard free decoder-only language modeling;
- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage.

## Next Gate

Move to a stronger matched decoder-only transformer implementation or a materially different learned binding mechanism. Do not treat more small pointer-generator variants as claim-expanding evidence unless they produce free held-out original retrieval improvement without structural copy routing.
