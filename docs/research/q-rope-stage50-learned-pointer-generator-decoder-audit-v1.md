# PhaseWrap-RoPE Stage 50 Learned Pointer-Generator Decoder Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 50 tests whether the Stage 49 fixed copy-output repair survives when the output path is made learned again. It reuses the Stage 45-49 train-short/test-long row family and fair positional method set, then trains a single-query pointer-generator decoder with:

- token embeddings;
- learned query, key, and value projections;
- a learned vocab output projection;
- a learned positional scale;
- a learned copy/vocab mixture gate.

The audited method set remains:

- `rope_relative`
- `alibi`
- `sinusoidal`
- `no_position`
- `phasewrap_bias`
- `phasewrap_adapter`

This is still a bounded decoder audit, not production transformer evidence.

## Reviewer Command

```bash
python scripts/run_stage50_learned_pointer_generator_decoder_audit.py
```

This writes:

- `logs/automated_stage_gates/stage50_learned_pointer_generator_decoder_audit/manifest.json`
- `logs/automated_stage_gates/stage50_learned_pointer_generator_decoder_audit/results.json`
- `logs/automated_stage_gates/stage50_learned_pointer_generator_decoder_audit/summary.csv`
- `logs/automated_stage_gates/stage50_learned_pointer_generator_decoder_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage50_learned_pointer_generator_decoder_audit/failed_runs.json`

## Result

Stage 50 records `LEARNED_POINTER_GENERATOR_RETRIEVAL_REPAIR_FAILED`.

The learned pointer-generator does not preserve the Stage 49 exact-offset copy repair. It learns a high copy gate across tasks, but neither retrieval lane reaches the `0.50` held-out top-1 threshold.

| Task | Best method | Test top-1 | Test MRR | Test target probability | Mean copy gate |
| --- | --- | ---: | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | 0.900000 | 0.900781 | 0.794922 | 0.924318 |
| `phase_cued_retrieval` | `no_position` | 0.100000 | 0.165206 | 0.023878 | 0.922514 |
| `exact_offset_passkey` | `sinusoidal` | 0.100000 | 0.296557 | 0.035865 | 0.922690 |

PhaseWrap rows remain bounded:

| Task | Method | Test top-1 | Test MRR | Test target probability |
| --- | --- | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `phasewrap_bias` | 0.850000 | 0.875781 | 0.779085 |
| `tiny_text_fact_qa` | `phasewrap_adapter` | 0.850000 | 0.875781 | 0.778954 |
| `phase_cued_retrieval` | `phasewrap_adapter` | 0.050000 | 0.150153 | 0.030653 |
| `phase_cued_retrieval` | `phasewrap_bias` | 0.050000 | 0.139604 | 0.029568 |
| `exact_offset_passkey` | `phasewrap_bias` | 0.000000 | 0.088056 | 0.023889 |
| `exact_offset_passkey` | `phasewrap_adapter` | 0.000000 | 0.084659 | 0.022876 |

No runs failed.

## Interpretation

Stage 50 narrows the Stage 49 repair. Fixed copy output can expose exact-offset retrieval for `rope_relative`, but a learned pointer-generator with the same row family does not keep that repair under the default bounded training budget.

This supports a sharper failure mode:

- the learned decoder can use copy mass enough to improve tiny text-fact QA;
- retrieval remains weak once attention and copy/vocab mixing are learned jointly;
- the Stage 49 exact-offset repair should not be treated as solved learned value generation;
- PhaseWrap-derived methods remain in the fair comparison set, but they do not lead this learned decoder audit.

## Claim Boundary

Supported:

- five-seed learned pointer-generator decoder evidence on the Stage 45-49 row family;
- evidence that the Stage 49 fixed-copy exact-offset repair does not survive this learned pointer-generator audit;
- preservation of tiny text-fact QA positives and retrieval failures;
- preservation of PhaseWrap failure modes under the fair method set.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that Stage 49 or Stage 50 solves free learned value generation.
