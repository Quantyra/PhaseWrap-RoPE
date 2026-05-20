# PhaseWrap-RoPE Stage 28 RULER-Style Attention-Bridge Benchmark v1

Date: `2026-05-20`

Status: `complete`

## Purpose

Stage 28 moves the roadmap one step closer to standard retrieval evidence. It trains a one-hidden-layer attention bridge directly on the Stage 12 non-phase-cued passkey, multi-needle, and aggregation-style retrieval rows across five deterministic model initialization seeds.

Targets are selected by explicit retrieval rules, not by the PhaseWrap score. The benchmark is still compact: it is not a full decoder-only language-model benchmark and does not prove that PhaseWrap-RoPE replaces RoPE.

## Command

```bash
python scripts/run_stage28_ruler_attention_bridge.py
```

## Artifacts

- `logs/automated_stage_gates/stage28_ruler_attention_bridge/manifest.json`
- `logs/automated_stage_gates/stage28_ruler_attention_bridge/results.json`
- `logs/automated_stage_gates/stage28_ruler_attention_bridge/summary.csv`
- `logs/automated_stage_gates/stage28_ruler_attention_bridge/per_run_results.csv`
- `logs/automated_stage_gates/stage28_ruler_attention_bridge/task_summary.csv`
- `logs/automated_stage_gates/stage28_ruler_attention_bridge/weak_runs.json`

## Current Result

Held-out test rows use length `1024`; train rows use lengths `128` and `256`. Each method is trained across five model initialization seeds.

| Method | Mean top-1 | Mean MRR | Mean target probability | Top-1 ECE |
| --- | ---: | ---: | ---: | ---: |
| `rope_relative` | `1.000000` | `1.000000` | `0.704867` | `0.297454` |
| `phasewrap_distance_adapter` | `1.000000` | `1.000000` | `0.518441` | `0.486407` |
| `sinusoidal` | `0.666667` | `0.825000` | `0.467632` | `0.150952` |
| `phasewrap_residual_adapter` | `0.450000` | `0.673611` | `0.322028` | `0.203495` |
| `no_position` | `0.050000` | `0.118035` | `0.037879` | `0.021380` |
| `phasewrap_score` | `0.016667` | `0.080860` | `0.045641` | `0.013257` |
| `alibi` | `0.000000` | `0.153196` | `0.037945` | `0.029264` |

`phasewrap_distance_adapter` matches `rope_relative` on top-1 and MRR for this compact retrieval bridge. `rope_relative` remains better calibrated by mean target probability, target-probability MAE, and top-1 expected calibration error. The fixed `phasewrap_score` remains weak.

## Interpretation

Stage 28 is constructive evidence that a PhaseWrap-plus-distance adapter can solve this compact non-phase-cued retrieval bridge by argmax ranking. It also preserves the current replacement gap because the RoPE-like baseline has higher target probability and the experiment is still not a full transformer benchmark.

Supported:

- compact non-phase-cued retrieval bridge over passkey, multi-needle, and aggregation-style rows;
- multiple initialization seeds and confidence intervals over seed-level ranking, probability, and calibration metrics;
- explicit weak-run reporting.

Not supported:

- production transformer superiority;
- full transformer-scale validation;
- a claim that PhaseWrap-RoPE replaces RoPE;
- quantum advantage or hardware-model advantage.

## Next Step

The next stronger experiment remains the full roadmap milestone: put the retrieval structure into a matched small decoder-only transformer or standard retrieval/QA harness with RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap variants, at least five seeds, confidence intervals, failed-run artifacts, and tasks whose answers are not constructed from the PhaseWrap score.
