# PhaseWrap-RoPE Stage 73 Phase-Cued Period-Pair Support Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 73 tests whether the Stage 72 phase-cued support miss is specific to the default 8/12 period pair or persists across the predeclared Stage 11 period-pair grid.

For each fixed period pair, the audit scores every prefix position in the original Stage 10 phase-cued rows, collects positions tied for maximum score, and copies uniformly over that max-score support.

This is not a learned decoder and not a post-hoc promotion benchmark.

## Reviewer Command

```bash
python scripts/run_stage73_phase_cued_period_pair_support_audit.py
```

This writes:

- `logs/automated_stage_gates/stage73_phase_cued_period_pair_support_audit/manifest.json`
- `logs/automated_stage_gates/stage73_phase_cued_period_pair_support_audit/results.json`
- `logs/automated_stage_gates/stage73_phase_cued_period_pair_support_audit/summary.csv`
- `logs/automated_stage_gates/stage73_phase_cued_period_pair_support_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage73_phase_cued_period_pair_support_audit/per_example_results.csv`
- `logs/automated_stage_gates/stage73_phase_cued_period_pair_support_audit/failed_runs.json`

## Result

Stage 73 records `PHASE_CUED_PERIOD_PAIR_SWEEP_DOES_NOT_REPAIR_SUPPORT`.

Every tested period pair has held-out target-in-max-support rate `0.000000`. The best held-out top-1 is `0.033333`, from `12/24`, still far below the `0.500000` generalization threshold.

| Period pair | Fundamental period | Held-out top-1 | Target in max support | Mean max support count |
| --- | ---: | ---: | ---: | ---: |
| `12/24` | 24 | 0.033333 | 0.000000 | 4.550000 |
| `10/16` | 80 | 0.016667 | 0.000000 | 1.216667 |
| `4/8` | 8 | 0.016667 | 0.000000 | 14.000000 |
| `16/32` | 32 | 0.016667 | 0.000000 | 3.350000 |
| `7/11` | 77 | 0.016667 | 0.000000 | 2.550000 |
| `8/12` | 24 | 0.016667 | 0.000000 | 4.500000 |

No runs failed.

## Interpretation

Stage 73 strengthens the phase-cued failure boundary. The Stage 72 miss is not repaired by swapping among the predeclared Stage 11 period pairs.

This means the current original phase-cued target rule is not directly captured by the tested fixed PhaseWrap max-score supports. A later mechanism could still learn an additional rule, but the current fixed-score family does not justify a RoPE-replacement claim.

## Claim Boundary

Supported:

- evidence that the tested fixed PhaseWrap period pairs do not put the held-out phase-cued target in max-score support;
- evidence that the default `8/12` miss is not unique among the tested period pairs;
- fair no-training reporting over the predeclared period-pair grid.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that period-pair selection after seeing held-out rows is promotion evidence;
- a claim that fixed-score support is learned decoder-only transformer behavior.

## Next Gate

The next gate should either redesign the original phase-cued mechanism around standard-input inference, or explicitly mark this row family as adversarial to the current fixed PhaseWrap support family before returning to stronger matched decoder-only transformer evidence.
