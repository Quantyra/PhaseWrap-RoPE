# PhaseWrap-RoPE Stage 48 Adam Decoder Stability Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 48 tests whether the Stage 47 one-seed PhaseWrap-positive tiny text-fact QA result is stable across the standard five model/data seeds. It keeps the Stage 47 Adam one-block decoder harness, fair method set, tasks, and artifact discipline.

The audited method set remains:

- `rope_relative`
- `alibi`
- `sinusoidal`
- `no_position`
- `phasewrap_bias`
- `phasewrap_adapter`

## Reviewer Command

```bash
python scripts/run_stage48_adam_decoder_stability_audit.py
```

This writes:

- `logs/automated_stage_gates/stage48_adam_decoder_stability_audit/manifest.json`
- `logs/automated_stage_gates/stage48_adam_decoder_stability_audit/results.json`
- `logs/automated_stage_gates/stage48_adam_decoder_stability_audit/summary.csv`
- `logs/automated_stage_gates/stage48_adam_decoder_stability_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage48_adam_decoder_stability_audit/failed_runs.json`

## Result

Stage 48 records `TINY_QA_POSITIVE_NOT_PHASEWRAP_STABLE_RETRIEVAL_FAILED`.

Across five seeds, tiny text-fact QA remains a positive lane for the one-block Adam decoder, but the Stage 47 PhaseWrap lead does not hold:

| Task | Method | Seeds | Test top-1 | Test MRR | Test target probability |
| --- | --- | ---: | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `rope_relative` | 5 | 0.500000 | 0.651572 | 0.490031 |
| `tiny_text_fact_qa` | `no_position` | 5 | 0.500000 | 0.651572 | 0.485697 |
| `tiny_text_fact_qa` | `alibi` | 5 | 0.450000 | 0.626572 | 0.467467 |
| `tiny_text_fact_qa` | `sinusoidal` | 5 | 0.450000 | 0.626572 | 0.458315 |
| `tiny_text_fact_qa` | `phasewrap_bias` | 5 | 0.450000 | 0.626569 | 0.450169 |
| `tiny_text_fact_qa` | `phasewrap_adapter` | 5 | 0.450000 | 0.626569 | 0.449552 |

Both retrieval lanes still fail held-out top-1 for every method:

- `phase_cued_retrieval`: best test top-1 `0.000000`;
- `exact_offset_passkey`: best test top-1 `0.000000`.

## Interpretation

Stage 48 narrows the Stage 47 positive. The tiny text-fact QA lane is a real partial generalization result for the Adam one-block decoder, but it is not a stable PhaseWrap lead across seeds. The retrieval failure remains the main blocker for any broader RoPE-replacement claim.

This supports a more precise boundary:

- PhaseWrap-derived methods remain viable enough to keep in the fair comparison set.
- The one-seed Stage 47 PhaseWrap lead should not be cited as stable.
- The current matched one-block decoder evidence does not promote PhaseWrap-RoPE over RoPE-like or no-position baselines.

## Claim Boundary

Supported:

- five-seed Adam decoder stability evidence;
- positive tiny text-fact QA generalization for the one-block Adam decoder;
- evidence that the Stage 47 PhaseWrap tiny text-fact QA lead is not stable across seeds;
- negative retrieval-generalization evidence for every tested method.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that the Stage 47 one-seed PhaseWrap tiny text-fact QA lead is stable.
