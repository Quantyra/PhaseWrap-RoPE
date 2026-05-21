# PhaseWrap-RoPE Stage 79 Support-Complete Auxiliary Copy Head Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 79 tests the next gate implied by Stage 78: rerun the Stage 77 auxiliary support/copy path after restoring same-seed phase-cued support coverage.

The audit uses `examples_per_length=6`, matching the earlier support-complete exposure convention, and trains one same-seed auxiliary support/copy head per seed and method. This removes the zero-coverage confound from Stage 77 while preserving the same compact copy-readout limitation.

This is still not a matched decoder-only transformer.

## Reviewer Command

```bash
python scripts/run_stage79_support_complete_auxiliary_copy_head_audit.py
```

This writes:

- `logs/automated_stage_gates/stage79_support_complete_auxiliary_copy_head_audit/manifest.json`
- `logs/automated_stage_gates/stage79_support_complete_auxiliary_copy_head_audit/results.json`
- `logs/automated_stage_gates/stage79_support_complete_auxiliary_copy_head_audit/summary.csv`
- `logs/automated_stage_gates/stage79_support_complete_auxiliary_copy_head_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage79_support_complete_auxiliary_copy_head_audit/failed_runs.json`

## Result

Stage 79 records `SUPPORT_COMPLETE_AUXILIARY_COPY_HEAD_SUPPORT_RECOVERED_RETRIEVAL_FAILED`.

| Task | Best method | Test top-1 | Test target probability |
| --- | --- | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | 1.000000 | 0.748539 |
| `phase_cued_retrieval` | `phasewrap_adapter` | 0.016667 | 0.065183 |
| `exact_offset_passkey` | `sinusoidal` | 0.650000 | 0.340343 |

Mean held-out phase-cued support accuracy is `1.000000`. No runs failed.

## Interpretation

Stage 79 separates support recovery from token retrieval. Once same-seed support coverage is restored, the auxiliary support head recovers the held-out phase-cued support labels perfectly. The phase-cued token-copy task still fails: best held-out top-1 is only `0.016667`.

This means Stage 77's zero support accuracy was explained by Stage 78's coverage finding, but restoring coverage is still not enough. The remaining blocker is using recovered support inside the compact copy-readout path to select the target token.

The exact-offset lane is solved by `sinusoidal` in this support-complete setting, not by a PhaseWrap method.

## Claim Boundary

Supported:

- evidence that support-complete same-seed exposure recovers held-out phase-cued support labels;
- evidence that recovered support labels still do not repair phase-cued token retrieval in the compact auxiliary copy-head;
- fair reporting across RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap variants.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that this compact support-complete auxiliary copy-head is a matched decoder-only transformer;
- a claim that support-complete auxiliary copy training supports positional-method promotion.

## Next Gate

The next gate should move beyond compact support/copy heads. A useful learned decoder must preserve recovered support and use it to select the copied target token under fair RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap comparisons.
