# PhaseWrap-RoPE Stage 51 Decoder-Path Plateau Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 51 audits the matched decoder path from Stages 45-50 as a claim-boundary checkpoint. It trains no new model. Instead, it reads the sealed manifests and failed-run artifacts for:

- Stage 45 matched one-block decoder-only gate;
- Stage 46 longer-training capacity audit;
- Stage 47 Adam decoder generalization audit;
- Stage 48 Adam decoder stability audit;
- Stage 49 fixed copy-decoder retrieval repair audit;
- Stage 50 learned pointer-generator decoder audit.

The question is whether this decoder path should keep broadening claims or be treated as a bounded plateau before moving to a materially stronger decoder-only transformer.

## Reviewer Command

```bash
python scripts/run_stage51_decoder_path_plateau_audit.py
```

This writes:

- `logs/automated_stage_gates/stage51_decoder_path_plateau_audit/manifest.json`
- `logs/automated_stage_gates/stage51_decoder_path_plateau_audit/results.json`
- `logs/automated_stage_gates/stage51_decoder_path_plateau_audit/summary.csv`

## Result

Stage 51 records `BOUND_DECODER_PATH_PLATEAU`.

| Stage | Decision | Retrieval generalized | PhaseWrap retrieval generalized | Tiny-text best | Failed runs |
| --- | --- | --- | --- | --- | ---: |
| Stage 45 | `PROMOTION_NOT_SUPPORTED` | none | none | none | 0 |
| Stage 46 | `CAPACITY_NOT_ESTABLISHED` | none | none | `phasewrap_adapter` | 0 |
| Stage 47 | `TRAIN_FIT_WITH_PARTIAL_GENERALIZATION` | none | none | `phasewrap_bias` | 0 |
| Stage 48 | `TINY_QA_POSITIVE_NOT_PHASEWRAP_STABLE_RETRIEVAL_FAILED` | none | none | `rope_relative` | 0 |
| Stage 49 | `COPY_DECODER_PARTIALLY_REPAIRS_RETRIEVAL` | `exact_offset_passkey` | none | `sinusoidal` | 0 |
| Stage 50 | `LEARNED_POINTER_GENERATOR_RETRIEVAL_REPAIR_FAILED` | none | none | `sinusoidal` | 0 |

## Interpretation

Stages 45-50 are useful evidence, but they now form a bounded decoder-path plateau:

- Adam optimizer hardening can establish train fit and tiny text-fact QA partial generalization.
- The one-seed PhaseWrap tiny text-fact QA lead does not survive five-seed stability.
- Fixed copy output can expose exact-offset retrieval for `rope_relative`.
- The fixed-copy repair does not survive the learned pointer-generator decoder audit.
- PhaseWrap does not lead any repaired retrieval lane.
- No failed runs were dropped from the audited path.

The next useful gate is not another one-block output-path variant. It is a materially stronger matched decoder-only transformer under the same RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap fair-comparison frame.

## Claim Boundary

Supported:

- bounded decoder-path evidence over Stages 45-50;
- bottleneck diagnosis separating optimizer, output-copy, and learned pointer-generator behavior;
- preservation of tiny text-fact QA positives and retrieval failures;
- a negative plateau decision for this one-block/pointer-generator path.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that the Stage 49 fixed-copy repair solves learned retrieval generation.
