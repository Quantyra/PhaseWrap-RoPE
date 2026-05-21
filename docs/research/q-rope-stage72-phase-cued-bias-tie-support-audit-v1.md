# PhaseWrap-RoPE Stage 72 Phase-Cued Bias Tie-Support Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 72 tests whether the original held-out phase-cued target appears in each method's maximum positional-bias support set.

Stage 71 used a single hard argmax. Stage 72 is tie-aware: it collects every prefix position tied for maximum positional bias, copies uniformly over those positions, and reports whether the true target position is in that max-bias set.

This is not a learned decoder. It is a no-training diagnostic for whether the phase-cued blocker can be explained by argmax tie-breaking.

## Reviewer Command

```bash
python scripts/run_stage72_phase_cued_bias_tie_support_audit.py
```

This writes:

- `logs/automated_stage_gates/stage72_phase_cued_bias_tie_support_audit/manifest.json`
- `logs/automated_stage_gates/stage72_phase_cued_bias_tie_support_audit/results.json`
- `logs/automated_stage_gates/stage72_phase_cued_bias_tie_support_audit/summary.csv`
- `logs/automated_stage_gates/stage72_phase_cued_bias_tie_support_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage72_phase_cued_bias_tie_support_audit/per_example_results.csv`
- `logs/automated_stage_gates/stage72_phase_cued_bias_tie_support_audit/failed_runs.json`

## Result

Stage 72 records `PHASE_CUED_TARGET_NOT_IN_PHASEWRAP_MAX_BIAS_SUPPORT`.

| Method | Held-out top-1 | Target in max-bias tie set | Mean max tie count | Mean target bias rank |
| --- | ---: | ---: | ---: | ---: |
| `no_position` | 0.066666 | 1.000000 | 55.000000 | 11.900000 |
| `rope_relative` | 0.016667 | 0.000000 | 1.000000 | 39.283333 |
| `phasewrap_adapter` | 0.016667 | 0.000000 | 1.866667 | 42.100000 |
| `phasewrap_bias` | 0.016667 | 0.000000 | 4.500000 | 29.083333 |
| `alibi` | 0.000000 | 0.000000 | 1.000000 | 44.100000 |
| `sinusoidal` | 0.000000 | 0.000000 | 1.833333 | 8.683333 |

No runs failed.

## Interpretation

Stage 72 rules out a narrow escape hatch for the current PhaseWrap failure on original phase-cued rows.

The issue is not merely that Stage 71 picked the wrong representative among tied maximum-bias positions. For `phasewrap_bias` and `phasewrap_adapter`, the held-out target is not in the max-bias tie set at all. `no_position` includes the target only because every prefix position is tied, creating high ambiguity rather than positional evidence.

This strengthens the honest boundary: current PhaseWrap positional bias does not directly identify the original held-out phase-cued target under the Stage 10 row construction.

## Claim Boundary

Supported:

- evidence that PhaseWrap max-bias support does not contain the held-out phase-cued target often enough to explain the blocker as tie-breaking;
- evidence that no-position all-support is ambiguous and not positional-method evidence;
- fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap reporting on unchanged original phase-cued rows.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that tie-aware support is learned decoder-only transformer behavior;
- a claim that no-position all-support ambiguity is positional-method evidence.

## Next Gate

The next gate should test whether a non-oracle, matched mechanism can infer the phase-cued target rule from standard inputs or whether the original phase-cued row family should be treated as adversarial to the current fixed PhaseWrap bias.
