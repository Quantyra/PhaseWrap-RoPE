# PhaseWrap-RoPE Stage 49 Copy-Decoder Retrieval Repair Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 49 tests whether the Stage 45-48 matched one-block decoder retrieval failure is partly an output bottleneck. It reuses the same train-short/test-long rows and fair positional method set, but replaces the failed learned-vocab output path with copied prefix-token mass from a single-query decoder attention distribution.

The audited method set remains:

- `rope_relative`
- `alibi`
- `sinusoidal`
- `no_position`
- `phasewrap_bias`
- `phasewrap_adapter`

This is a repair audit, not promotion evidence by itself. It asks whether retrieval can generalize when the decoder has an explicit copy output, then preserves the method ordering and remaining failures.

## Reviewer Command

```bash
python scripts/run_stage49_copy_decoder_retrieval_repair_audit.py
```

This writes:

- `logs/automated_stage_gates/stage49_copy_decoder_retrieval_repair_audit/manifest.json`
- `logs/automated_stage_gates/stage49_copy_decoder_retrieval_repair_audit/results.json`
- `logs/automated_stage_gates/stage49_copy_decoder_retrieval_repair_audit/summary.csv`
- `logs/automated_stage_gates/stage49_copy_decoder_retrieval_repair_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage49_copy_decoder_retrieval_repair_audit/failed_runs.json`

## Result

Stage 49 records `COPY_DECODER_PARTIALLY_REPAIRS_RETRIEVAL`.

The copy decoder repairs the exact-offset passkey lane for `rope_relative`, makes tiny text-fact QA easy for all tested methods, and still fails to repair the phase-cued retrieval lane.

| Task | Best method | Test top-1 | Test MRR | Test target probability | ECE |
| --- | --- | ---: | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | 1.000000 | 1.000000 | 0.998000 | 0.002000 |
| `exact_offset_passkey` | `rope_relative` | 1.000000 | 1.000000 | 0.305822 | 0.694178 |
| `phase_cued_retrieval` | `sinusoidal` | 0.100000 | 0.207371 | 0.013302 | 0.463231 |

PhaseWrap rows remain bounded:

| Task | Method | Test top-1 | Test MRR | Test target probability |
| --- | --- | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `phasewrap_adapter` | 1.000000 | 1.000000 | 0.755837 |
| `tiny_text_fact_qa` | `phasewrap_bias` | 1.000000 | 1.000000 | 0.749889 |
| `exact_offset_passkey` | `phasewrap_adapter` | 0.000000 | 0.128953 | 0.025411 |
| `exact_offset_passkey` | `phasewrap_bias` | 0.000000 | 0.127286 | 0.024678 |
| `phase_cued_retrieval` | `phasewrap_bias` | 0.050000 | 0.154273 | 0.019421 |
| `phase_cued_retrieval` | `phasewrap_adapter` | 0.050000 | 0.149403 | 0.019258 |

No runs failed.

## Interpretation

Stage 49 narrows the Stage 45-48 negative result. The matched one-block decoder failure was not only about positional mechanisms: when the output path can copy prefix tokens, exact-offset passkey retrieval becomes solvable for RoPE-relative scoring. The phase-cued retrieval lane remains weak even with copy output, and PhaseWrap variants do not lead the repaired retrieval lane.

The result therefore supports output-bottleneck diagnosis, not a PhaseWrap promotion:

- copy-style value output can expose retrieval behavior hidden by the learned-vocab bottleneck;
- RoPE-relative, not PhaseWrap, is strongest on the repaired exact-offset retrieval lane;
- phase-cued retrieval remains unresolved in this matched repair harness;
- tiny text-fact QA is no longer discriminative once a content span matcher and copy output are present.

## Claim Boundary

Supported:

- five-seed copy-decoder repair evidence on the Stage 45-48 row family;
- evidence that exact-offset retrieval can generalize after replacing learned vocab output with copied prefix-token mass;
- evidence that PhaseWrap does not lead the repaired retrieval lane;
- preservation of phase-cued retrieval failure under the repair.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that copy-output repair is equivalent to free learned value generation.
