# PhaseWrap-RoPE Stage 63 Two-Block Copy-Output Capacity Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 63 tests whether the Stage 62 learned vocab-softmax output path is the immediate capacity blocker.

It keeps the support-complete Stage 61/62 row setup and the fair method set:

- RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons;
- all five default seeds;
- `examples_per_length = 6`;
- `80` training epochs;
- two learned q/k/v/o attention blocks;
- no lookup output and no fallback cue decoder.

The change is the output path: Stage 63 removes the learned full-vocab softmax projection and copies probability mass from learned second-block attention to observed prefix token IDs.

## Reviewer Command

```bash
python scripts/run_stage63_two_block_copy_output_capacity_audit.py
```

This writes:

- `logs/automated_stage_gates/stage63_two_block_copy_output_capacity_audit/manifest.json`
- `logs/automated_stage_gates/stage63_two_block_copy_output_capacity_audit/results.json`
- `logs/automated_stage_gates/stage63_two_block_copy_output_capacity_audit/summary.csv`
- `logs/automated_stage_gates/stage63_two_block_copy_output_capacity_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage63_two_block_copy_output_capacity_audit/failed_runs.json`

## Result

Stage 63 records `TWO_BLOCK_COPY_OUTPUT_CAPACITY_WITHOUT_RETRIEVAL_GENERALIZATION`.

Copy output establishes train capacity: the best train top-1 is `1.000000`, above the `0.750000` threshold. It does not establish retrieval generalization: both retrieval lanes have best held-out top-1 `0.050000`, below the `0.500000` threshold.

| Task | Best train method | Best train top-1 | Best test method | Best test top-1 |
| --- | --- | ---: | --- | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | 1.000000 | `sinusoidal` | 0.600000 |
| `phase_cued_retrieval` | `sinusoidal` | 1.000000 | `phasewrap_bias` / `phasewrap_adapter` / `sinusoidal` | 0.050000 |
| `exact_offset_passkey` | `sinusoidal` / `rope_relative` | 1.000000 | `rope_relative` / `no_position` | 0.050000 |

No runs failed.

## Interpretation

Stage 63 is a useful positive capacity result but not promotion evidence. It shows that the two-block attention path can fit the support-complete rows when the output path is changed to copied prefix-token mass.

The failure mode also remains clear: copy-output capacity does not make held-out retrieval generalize. PhaseWrap-derived methods tie or lead weak phase-cued held-out ranking at `0.050000`, but that is far below the promotion threshold, and `sinusoidal`, `rope_relative`, and `no_position` remain competitive in different lanes.

The next useful gate should keep the capacity-positive output lesson while testing a standard learned output path or stronger architecture that can generalize retrieval without treating copy output as RoPE-replacement evidence.

## Claim Boundary

Supported:

- evidence that learned two-block attention plus copy output can establish train capacity;
- evidence that the Stage 62 full-vocab softmax path was an immediate capacity bottleneck;
- evidence that output-path repair still does not establish held-out retrieval generalization;
- fair reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants;
- failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that copy-output repair is equivalent to free learned value generation;
- a claim that Stage 63 is positional-method promotion evidence.
