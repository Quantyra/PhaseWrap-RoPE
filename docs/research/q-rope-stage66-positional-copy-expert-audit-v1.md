# PhaseWrap-RoPE Stage 66 Positional-Copy Expert Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 66 tests whether the Stage 64/65 retrieval-generalization failure is mainly a learned-attention routing problem.

It keeps the Stage 64 two-block learned pointer-generator path and adds a direct positional-copy expert:

- RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons;
- all five default seeds;
- `examples_per_length = 6`;
- `80` training epochs;
- two learned q/k/v/o attention blocks;
- learned mixture of full-vocab softmax generation and learned copied prefix-token mass;
- learned mixture with a direct copy distribution computed from the same positional bias available to the tested method.

This is a mechanism diagnostic. It is not a full decoder-only language-model validation and not positional-method promotion evidence.

## Reviewer Command

```bash
python scripts/run_stage66_positional_copy_expert_audit.py
```

This writes:

- `logs/automated_stage_gates/stage66_positional_copy_expert_audit/manifest.json`
- `logs/automated_stage_gates/stage66_positional_copy_expert_audit/results.json`
- `logs/automated_stage_gates/stage66_positional_copy_expert_audit/summary.csv`
- `logs/automated_stage_gates/stage66_positional_copy_expert_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage66_positional_copy_expert_audit/failed_runs.json`

## Result

Stage 66 records `POSITIONAL_COPY_EXPERT_WITHOUT_RETRIEVAL_GENERALIZATION`.

The positional-copy expert preserves train capacity: the best train top-1 is `1.000000`, above the `0.750000` threshold. It does not establish retrieval generalization: phase-cued retrieval reaches only `0.033333` best held-out top-1, and exact-offset passkey reaches only `0.050000` best held-out top-1.

| Task | Best train method | Best train top-1 | Best test method | Best test top-1 |
| --- | --- | ---: | --- | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | 1.000000 | `sinusoidal` | 0.583334 |
| `phase_cued_retrieval` | `sinusoidal` | 0.983333 | `sinusoidal` | 0.033333 |
| `exact_offset_passkey` | `phasewrap_bias` | 1.000000 | `rope_relative` | 0.050000 |

No runs failed.

## Interpretation

Stage 66 is negative for the direct-expert repair hypothesis. A direct positional-copy expert improves the output path available to every method, but held-out retrieval remains far below the `0.500000` generalization threshold.

This sharpens the blocker: the current row family is not repaired by output-path capacity, length-40 curriculum, or a direct method-bias copy expert. The next useful work needs a stronger retrieval architecture, different data design, or a more explicit mechanism for inferring retrieval cues from standard inputs before positional-method promotion is evaluated.

## Claim Boundary

Supported:

- evidence that a direct method-bias positional-copy expert preserves train capacity;
- evidence that the expert still does not establish held-out retrieval generalization;
- fair reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants;
- failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that a direct positional-copy expert is full decoder-only language-model validation;
- a claim that Stage 66 is positional-method promotion evidence.
