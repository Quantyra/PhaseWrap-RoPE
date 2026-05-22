# PhaseWrap-RoPE Stage 105 Independent Rerun Protocol v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 105 closes the pre-execution rerun-design gap for the noisy-hardware robustness goal.

Stage 103 preregisters the metric rule. Stage 104 prepares all matched packet execution templates. Stage 105 now preregisters how independent backend/date/calibration reruns must be handled before any robustness claim can be made beyond a single recorded hardware window.

## Reviewer Command

```bash
python scripts/run_stage105_independent_rerun_protocol.py
```

This writes:

- `logs/automated_stage_gates/stage105_independent_rerun_protocol/manifest.json`
- `logs/automated_stage_gates/stage105_independent_rerun_protocol/results.json`
- `logs/automated_stage_gates/stage105_independent_rerun_protocol/summary.csv`
- `logs/automated_stage_gates/stage105_independent_rerun_protocol/rerun_windows.json`

## Result

Current decision:

`INDEPENDENT_RERUN_PROTOCOL_PREREGISTERED_EXECUTION_REQUIRED`

The protocol requires:

- at least `2` independent windows per provider;
- at least `24` hours between provider windows after the first;
- fresh Stage 101 known-state calibration for each provider/backend/date window;
- all Stage 104 packet execution templates for that provider in each window;
- Stage 103 metric recomputation independently inside each window.

Current providers:

- `amazon_braket`
- `ibm_runtime`

Current rerun windows:

- `amazon_braket__independent_window_00`
- `amazon_braket__independent_window_01`
- `ibm_runtime__independent_window_00`
- `ibm_runtime__independent_window_01`

## Aggregation Rule

A PhaseWrap robustness advantage may only be described as replicated if the Stage 103 advantage rule holds in every independent window for the same provider, source lane, and circuit template.

Reports must include:

- per-window metric tables;
- across-window median and range for PhaseWrap and comparator errors;
- failures, missing packets, calibration failures, queue metadata, backend metadata, and calibration timestamps without exclusion.

## Claim Boundary

Supported:

- a preregistered independent rerun protocol for the matched noisy-hardware comparison;
- a minimum two-window provider/backend/date calibration requirement;
- an aggregation rule preventing single-window noisy-hardware advantage claims.

Excluded:

- completed independent reruns;
- real hardware evidence;
- a PhaseWrap robustness advantage claim;
- provider-wide robustness beyond recorded windows.

## Next Gate

Run Stage 101 calibration and all Stage 104 matched packet executions in each independent provider window, then recompute Stage 103 metrics per window and aggregate only under the Stage 105 rule.
