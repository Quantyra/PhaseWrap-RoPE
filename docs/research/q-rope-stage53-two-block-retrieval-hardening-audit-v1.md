# PhaseWrap-RoPE Stage 53 Two-Block Retrieval Hardening Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 53 tests whether the Stage 52 two-block decoder feasibility result improves when the same stronger decoder receives more retrieval exposure and a larger training budget. It keeps the same fair positional method set:

- `rope_relative`
- `alibi`
- `sinusoidal`
- `no_position`
- `phasewrap_bias`
- `phasewrap_adapter`

This remains a one-seed hardening audit. It does not satisfy the five-seed promotion standard.

## Reviewer Command

```bash
python scripts/run_stage53_two_block_retrieval_hardening_audit.py
```

This writes:

- `logs/automated_stage_gates/stage53_two_block_retrieval_hardening_audit/manifest.json`
- `logs/automated_stage_gates/stage53_two_block_retrieval_hardening_audit/results.json`
- `logs/automated_stage_gates/stage53_two_block_retrieval_hardening_audit/summary.csv`
- `logs/automated_stage_gates/stage53_two_block_retrieval_hardening_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage53_two_block_retrieval_hardening_audit/failed_runs.json`

## Result

Stage 53 records `TWO_BLOCK_RETRIEVAL_HARDENING_FAILED`.

| Task | Best method | Train top-1 | Test top-1 | Test MRR | Test target probability |
| --- | --- | ---: | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | 0.500000 | 0.500000 | 0.750000 | 0.499694 |
| `phase_cued_retrieval` | `sinusoidal` | 0.500000 | 0.000000 | 0.024871 | 0.000003 |
| `exact_offset_passkey` | `sinusoidal` | 0.750000 | 0.000000 | 0.026144 | 0.000009 |

PhaseWrap rows remain bounded:

| Task | Method | Train top-1 | Test top-1 | Test MRR | Test target probability |
| --- | --- | ---: | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `phasewrap_bias` | 0.500000 | 0.500000 | 0.750000 | 0.499694 |
| `tiny_text_fact_qa` | `phasewrap_adapter` | 0.500000 | 0.500000 | 0.750000 | 0.499694 |
| `phase_cued_retrieval` | `phasewrap_adapter` | 0.500000 | 0.000000 | 0.023037 | 0.000005 |
| `phase_cued_retrieval` | `phasewrap_bias` | 0.500000 | 0.000000 | 0.016883 | 0.000004 |
| `exact_offset_passkey` | `phasewrap_bias` | 0.250000 | 0.000000 | 0.017467 | 0.000006 |
| `exact_offset_passkey` | `phasewrap_adapter` | 0.250000 | 0.000000 | 0.017467 | 0.000006 |

No runs failed.

## Interpretation

Stage 53 does not repair retrieval. Increasing exposure and training budget in this two-block autograd harness still leaves both retrieval lanes at zero held-out top-1. It also weakens the Stage 52 tiny text-fact QA result, so this exact hardening direction should not be treated as a scale-up path.

The current boundary remains:

- retrieval generalization is still the blocker;
- PhaseWrap does not lead a retrieval lane;
- one-seed two-block hardening does not support promotion;
- the result is useful negative evidence for this in-repo stronger decoder direction.

## Claim Boundary

Supported:

- one-seed retrieval-hardening evidence for the Stage 52 two-block decoder;
- negative evidence that this exposure/training-budget hardening does not repair retrieval;
- preservation of PhaseWrap failure modes under the fair method set.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that Stage 53 satisfies the five-seed promotion standard.
