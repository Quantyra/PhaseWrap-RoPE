# PhaseWrap-RoPE Stage 56 Standard-Input Cue-Copy Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 56 tests how much of the Stage 55 row-metadata upper bound survives when cue-copy features are derived only from visible input tokens:

- retrieval rows use the query token's encoded `reference_delta mod 16`;
- tiny text-fact QA uses visible query entity tokens and visible fact spans;
- `row.reference_delta`, `row.target_delta`, and `row.target_pos` are not used by the cue-copy diagnostic.

This remains a deterministic copy-output diagnostic, not a learned decoder-only transformer result or promotion evidence.

## Reviewer Command

```bash
python scripts/run_stage56_standard_input_cue_copy_audit.py
```

This writes:

- `logs/automated_stage_gates/stage56_standard_input_cue_copy_audit/manifest.json`
- `logs/automated_stage_gates/stage56_standard_input_cue_copy_audit/results.json`
- `logs/automated_stage_gates/stage56_standard_input_cue_copy_audit/summary.csv`
- `logs/automated_stage_gates/stage56_standard_input_cue_copy_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage56_standard_input_cue_copy_audit/failed_runs.json`

## Result

Stage 56 records `STANDARD_INPUT_CUE_COPY_PARTIAL_RETRIEVAL`.

| Task | Best method | Test top-1 | Test target probability |
| --- | --- | ---: | ---: |
| `tiny_text_fact_qa` | `rope_relative` | 1.000000 | 1.000000 |
| `phase_cued_retrieval` | `sinusoidal` | 0.100000 | 0.058566 |
| `exact_offset_passkey` | `rope_relative` | 0.650000 | 0.604881 |

No runs failed.

## Interpretation

Visible-token cue-copy features preserve only part of the Stage 55 metadata upper bound. Tiny text-fact QA is solved from visible entity/fact spans, and exact-offset passkey is partially repaired for `rope_relative`, but phase-cued retrieval remains weak.

This keeps the promotion blocker intact. The full Stage 55 repair required explicit row metadata; decoding only standard input tokens does not recover the phase-cued retrieval rule.

## Claim Boundary

Supported:

- evidence about standard-input cue recovery after the Stage 55 metadata upper bound;
- fair method reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants;
- failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that visible query-token cue decoding is a learned decoder-only transformer result;
- a claim that this deterministic cue-copy diagnostic is positional-method promotion evidence.
