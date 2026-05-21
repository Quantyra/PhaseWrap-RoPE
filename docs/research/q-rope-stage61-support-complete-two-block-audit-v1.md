# PhaseWrap-RoPE Stage 61 Support-Complete Two-Block Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 61 tests whether the learned two-block decoder path improves when the phase-cued train split covers every reference-delta support residue for every seed.

This moves back from deterministic lookup/copy diagnostics to a learned decoder with:

- learned token embeddings;
- two q/k/v/o attention blocks;
- learned vocab softmax output;
- matched RoPE/ALiBI/sinusoidal/no-position/PhaseWrap method variants;
- no fixed copy output, no lookup output, and no fallback cue decoder.

## Reviewer Command

```bash
python scripts/run_stage61_support_complete_two_block_audit.py
```

This writes:

- `logs/automated_stage_gates/stage61_support_complete_two_block_audit/manifest.json`
- `logs/automated_stage_gates/stage61_support_complete_two_block_audit/results.json`
- `logs/automated_stage_gates/stage61_support_complete_two_block_audit/summary.csv`
- `logs/automated_stage_gates/stage61_support_complete_two_block_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage61_support_complete_two_block_audit/failed_runs.json`

## Result

Stage 61 records `SUPPORT_COMPLETE_TWO_BLOCK_CAPACITY_NOT_ESTABLISHED`.

All five default seeds have complete phase-cued held-out support coverage from train rows (`test_known_fraction = 1.0`). Despite that, the learned decoder does not establish capacity.

| Task | Best method | Train top-1 | Test top-1 | Test target probability |
| --- | --- | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | 0.166667 | 0.166667 | 0.165434 |
| `phase_cued_retrieval` | `no_position` | 0.150000 | 0.000000 | 0.004100 |
| `exact_offset_passkey` | `no_position` | 0.183333 | 0.016667 | 0.004397 |

No runs failed.

## Interpretation

Stage 61 shows support coverage alone does not repair the learned decoder path. Even after every seed's train split covers all phase-cued support residues, the two-block learned vocab-softmax model remains below the capacity threshold and does not generalize retrieval.

This is stronger negative evidence than the lookup diagnostics: the blocker is not just missing support examples. The current learned decoder architecture or optimization path still fails before positional-method promotion can be evaluated.

## Claim Boundary

Supported:

- evidence that support-complete phase-cued train coverage does not establish learned two-block decoder capacity;
- fair reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants;
- failed-run retention;
- continued bounded framing of PhaseWrap-RoPE as an auditable compact mechanism with mixed toy downstream evidence.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that support-complete training alone solves learned retrieval generalization;
- a claim that Stage 61 is positional-method promotion evidence.
