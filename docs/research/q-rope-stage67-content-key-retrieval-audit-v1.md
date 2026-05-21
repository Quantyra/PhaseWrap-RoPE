# PhaseWrap-RoPE Stage 67 Content-Key Retrieval Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 67 tests whether the Stage 64-66 retrieval failure is specific to the phase-cued/exact-offset row family rather than the two-block pointer-generator harness as a whole.

It redesigns the retrieval rows around a standard visible content cue:

- the prefix contains a key/value pair;
- the query contains the matching key token;
- the model must copy the value token;
- held-out lengths remain `48` and `64`;
- positional `reference_delta` is non-oracular;
- RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons remain matched.

This is a row-design diagnostic. It is not the original phase-cued or exact-offset retrieval gate, and it is not positional-method promotion evidence by itself.

## Reviewer Command

```bash
python scripts/run_stage67_content_key_retrieval_audit.py
```

This writes:

- `logs/automated_stage_gates/stage67_content_key_retrieval_audit/manifest.json`
- `logs/automated_stage_gates/stage67_content_key_retrieval_audit/results.json`
- `logs/automated_stage_gates/stage67_content_key_retrieval_audit/summary.csv`
- `logs/automated_stage_gates/stage67_content_key_retrieval_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage67_content_key_retrieval_audit/failed_runs.json`

## Result

Stage 67 records `CONTENT_KEY_RETRIEVAL_SOLVABLE_FOR_ALL_METHODS_NOT_PROMOTION`.

The redesigned content-key row family is solved at held-out lengths by every tested method, including `no_position`.

| Task | Best train method | Best train top-1 | Best test method | Best test top-1 |
| --- | --- | ---: | --- | ---: |
| `content_key_retrieval` | `phasewrap_adapter` | 1.000000 | `phasewrap_bias` | 1.000000 |

All tested methods reach held-out top-1 `1.000000` and MRR `1.000000`. The best target probability is slightly PhaseWrap-led (`phasewrap_bias` at `0.969954`), but `no_position` also solves top-1/MRR with target probability `0.967175`.

No runs failed.

## Interpretation

Stage 67 is positive evidence for the harness and negative evidence for claim expansion.

It shows that the two-block learned pointer-generator can generalize a standard visible content-key retrieval row design to held-out lengths. That narrows the Stage 64-66 blocker: the decoder path is not globally unable to retrieve. The unsolved blocker is the original phase-cued/exact-offset row family and the mechanism needed to infer those retrieval cues from standard inputs.

Because `no_position` solves the redesigned rows too, Stage 67 does not support a PhaseWrap-RoPE replacement claim or positional-method promotion.

## Claim Boundary

Supported:

- evidence that standard visible content-key retrieval is solvable by the current two-block pointer-generator harness;
- evidence that the earlier retrieval failure is row-family/mechanism-specific rather than a universal decoder inability;
- fair reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants;
- failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that content-key retrieval is equivalent to the original phase-cued/exact-offset gate;
- a claim that Stage 67 is positional-method promotion evidence.
