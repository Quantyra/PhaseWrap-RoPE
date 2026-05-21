# PhaseWrap-RoPE Stage 55 Row-Metadata Cue-Copy Upper-Bound Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 55 tests whether the Stage 52-54 retrieval rows are solvable when the decoder is given explicit row metadata that identifies the target-distance cue family. It keeps the same fair method set:

- `rope_relative`
- `alibi`
- `sinusoidal`
- `no_position`
- `phasewrap_bias`
- `phasewrap_adapter`

The output is deterministic copied prefix-token mass. The nonstandard diagnostic features are:

- exact match to `row.reference_delta`;
- modulo-24 congruence to `row.reference_delta`;
- normalized distance/farthest-position prior.

This is an upper-bound solvability audit, not promotion evidence. The row metadata is not a standard decoder-only input feature and no positional method should receive credit merely because the explicit cue-copy path solves the rows.

## Reviewer Command

```bash
python scripts/run_stage55_row_metadata_cue_copy_upper_bound_audit.py
```

This writes:

- `logs/automated_stage_gates/stage55_row_metadata_cue_copy_upper_bound_audit/manifest.json`
- `logs/automated_stage_gates/stage55_row_metadata_cue_copy_upper_bound_audit/results.json`
- `logs/automated_stage_gates/stage55_row_metadata_cue_copy_upper_bound_audit/summary.csv`
- `logs/automated_stage_gates/stage55_row_metadata_cue_copy_upper_bound_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage55_row_metadata_cue_copy_upper_bound_audit/failed_runs.json`

## Result

Stage 55 records `ROW_METADATA_CUE_COPY_UPPER_BOUND_SOLVES_RETRIEVAL_NOT_PROMOTION`.

| Task | Best method | Test top-1 | Test MRR | Test target probability |
| --- | --- | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | 1.000000 | 1.000000 | 0.999949 |
| `phase_cued_retrieval` | `rope_relative` | 0.900000 | 0.950000 | 0.471171 |
| `exact_offset_passkey` | `sinusoidal` | 1.000000 | 1.000000 | 0.999974 |

The same explicit cue-copy features also solve retrieval for `no_position`:

| Task | Method | Test top-1 | Test MRR | Test target probability |
| --- | --- | ---: | ---: | ---: |
| `phase_cued_retrieval` | `no_position` | 0.900000 | 0.950000 | 0.471171 |
| `exact_offset_passkey` | `no_position` | 1.000000 | 1.000000 | 0.999974 |

No runs failed.

## Interpretation

Stage 55 proves the Stage 52-54 row family is not inherently impossible: retrieval can generalize when the target-distance/congruence cue is explicitly exposed and output is copied from prefix-token mass.

It also blocks a stronger positional-method claim from this result. `no_position` solves the retrieval lanes under the same upper-bound features, and the best PhaseWrap rows do not uniquely lead. The result points to the next real gap: a matched decoder-only harness must learn or infer the retrieval cue from standard inputs instead of receiving `row.reference_delta` metadata directly.

## Claim Boundary

Supported:

- row-family solvability evidence under explicit row-metadata cue-copy features;
- evidence separating data impossibility from learned decoder mechanism failure;
- fair reporting across all positional methods with failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that explicit row metadata is a standard decoder-only input feature;
- a claim that this upper bound is positional-method promotion evidence.
