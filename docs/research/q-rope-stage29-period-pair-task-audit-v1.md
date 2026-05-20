# PhaseWrap-RoPE Stage 29 Period-Pair Task Audit v1

Date: `2026-05-20`

Status: `complete`

## Purpose

Stage 29 addresses a theory-to-task roadmap gap: whether another tested period pair makes the fixed phase-wrap score stronger on non-phase-cued retrieval rows.

The audit evaluates the Stage 11 period-pair grid on:

- Stage 12 local RULER-style retrieval rows: context lengths `128`, `256`, `512`, and `1024`;
- Stage 22 long-context retrieval rows: context lengths `512`, `1024`, `2048`, and `4096`.

Targets are selected by explicit passkey, multi-needle, and aggregation rules, not by maximizing any PhaseWrap score. No model is trained and no hardware is submitted.

## Command

```bash
python scripts/run_stage29_period_pair_task_audit.py
```

## Artifacts

- `logs/automated_stage_gates/stage29_period_pair_task_audit/manifest.json`
- `logs/automated_stage_gates/stage29_period_pair_task_audit/results.json`
- `logs/automated_stage_gates/stage29_period_pair_task_audit/local_summary.csv`
- `logs/automated_stage_gates/stage29_period_pair_task_audit/long_summary.csv`
- `logs/automated_stage_gates/stage29_period_pair_task_audit/task_summary.csv`
- `logs/automated_stage_gates/stage29_period_pair_task_audit/length_summary.csv`

## Current Result

Best local rows by top-1:

| Period pair | Top-1 | MRR | Target probability | Target top-tie rate |
| --- | ---: | ---: | ---: | ---: |
| `8/24` | `0.045833` | `0.163001` | `0.047964` | `0.058333` |
| `10/16` | `0.037500` | `0.158780` | `0.043671` | `0.037500` |
| `12/24` | `0.025000` | `0.124570` | `0.040160` | `0.029167` |
| `8/12` | `0.020833` | `0.156865` | `0.041892` | `0.033333` |

Best long-context rows by top-1:

| Period pair | Top-1 | MRR | Target probability | Target top-tie rate |
| --- | ---: | ---: | ---: | ---: |
| `9/15` | `0.016667` | `0.094350` | `0.022479` | `0.025000` |
| `8/12` | `0.012500` | `0.096153` | `0.024569` | `0.025000` |
| `10/16` | `0.012500` | `0.095165` | `0.026328` | `0.025000` |
| `8/16` | `0.012500` | `0.092551` | `0.027103` | `0.045833` |

No tested fixed period pair solves the non-phase-cued retrieval packets. Some pairs slightly improve top-1 over `8/12` on local rows, but all fixed-score top-1 values remain very low. On long-context rows, `9/15` has the highest top-1 in this grid, but the margin is small and the absolute score is still weak.

## Interpretation

Stage 29 strengthens the theory-to-task boundary:

- changing the fixed period pair alone does not close the retrieval gap;
- alias and target-score-gap diagnostics remain necessary when presenting any period-pair choice;
- the stronger evidence path remains an adapter or transformer mechanism that combines PhaseWrap features with distance/content information.

This audit does not prove any period pair is globally optimal and does not establish that PhaseWrap-RoPE replaces RoPE.
