# PhaseWrap-RoPE Stage 65 Pointer-Generator Length-Curriculum Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 65 tests whether the Stage 64 retrieval-generalization failure is mainly a length-exposure problem.

It keeps the Stage 64 learned pointer-generator output path and fair method set:

- RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons;
- all five default seeds;
- `examples_per_length = 6`;
- `80` training epochs;
- two learned q/k/v/o attention blocks;
- learned mixture of full-vocab softmax generation and copied prefix-token mass;
- no lookup output and no fallback cue decoder.

The change is curriculum exposure: the original length-40 validation rows are included in training, while lengths `48` and `64` remain held-out test rows.

## Reviewer Command

```bash
python scripts/run_stage65_pointer_generator_length_curriculum_audit.py
```

This writes:

- `logs/automated_stage_gates/stage65_pointer_generator_length_curriculum_audit/manifest.json`
- `logs/automated_stage_gates/stage65_pointer_generator_length_curriculum_audit/results.json`
- `logs/automated_stage_gates/stage65_pointer_generator_length_curriculum_audit/summary.csv`
- `logs/automated_stage_gates/stage65_pointer_generator_length_curriculum_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage65_pointer_generator_length_curriculum_audit/failed_runs.json`

## Result

Stage 65 records `POINTER_GENERATOR_LENGTH_CURRICULUM_WITHOUT_RETRIEVAL_GENERALIZATION`.

The length-40 curriculum preserves train capacity: the best train top-1 is `1.000000`, above the `0.750000` threshold. It does not establish retrieval generalization: phase-cued retrieval and exact-offset passkey each reach only `0.033333` best held-out top-1.

| Task | Best train method | Best train top-1 | Best test method | Best test top-1 |
| --- | --- | ---: | --- | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | 1.000000 | `sinusoidal` | 0.783333 |
| `phase_cued_retrieval` | `sinusoidal` | 0.966667 | `rope_relative` | 0.033333 |
| `exact_offset_passkey` | `sinusoidal` | 1.000000 | `sinusoidal` | 0.033333 |

No runs failed.

## Interpretation

Stage 65 improves tiny-text QA under length curriculum, but it does not repair retrieval. The best retrieval methods are RoPE-like or sinusoidal, not PhaseWrap-derived, and absolute held-out top-1 remains far below the `0.500000` generalization threshold.

This is useful negative evidence: the Stage 64 retrieval failure is not resolved by simply adding the intermediate length-40 rows to training.

## Claim Boundary

Supported:

- evidence that adding length-40 curriculum rows preserves train capacity;
- evidence that simple length curriculum still does not establish held-out retrieval generalization;
- evidence that tiny-text QA improves under the curriculum while retrieval remains weak;
- fair reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants;
- failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that validation-length curriculum training is the same as the original train-short/test-long gate;
- a claim that Stage 65 is positional-method promotion evidence.
