# PhaseWrap-RoPE Stage 102 Calibration Execution Package v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 102 turns the Stage 101 calibration blocker into a concrete execution evidence package.

Stage 101 says the matched Stage 99 and Stage 100 packet surfaces are frozen but cannot be interpreted until known-state raw counts pass bitstring-order calibration. Stage 102 emits provider-specific execution JSON templates and known-state preparation circuits for collecting that evidence.

## Reviewer Command

```bash
python scripts/run_stage102_calibration_execution_package.py
```

This writes:

- `logs/automated_stage_gates/stage102_calibration_execution_package/manifest.json`
- `logs/automated_stage_gates/stage102_calibration_execution_package/results.json`
- `logs/automated_stage_gates/stage102_calibration_execution_package/summary.csv`
- `logs/automated_stage_gates/stage102_calibration_execution_package/execution_templates/*.json`

## Result

Current decision:

`CALIBRATION_EXECUTION_TEMPLATES_PREPARED_COUNTS_STILL_REQUIRED`

Templates are generated for:

- `ibm_runtime_known_state_execution.json`
- `amazon_braket_known_state_execution.json`

Each template includes:

- required metadata fields;
- expected bitstring order;
- `|00>`, `|01>`, `|10>`, and `|11>` states;
- expected dominant measured key for each state;
- OpenQASM 3 preparation and measurement circuits;
- empty count placeholders that must be replaced with real hardware counts.

## Interpretation

Stage 102 is still no-hardware preparation. It does not complete calibration and does not allow Stage 99 or Stage 100 hardware results to be interpreted.

The next step is operational: execute the known-state circuits on the target provider/backend/date, fill the generated templates with real `job_or_task_ids`, backend metadata, timestamps, and raw counts, then rerun Stage 101 with `--execution-dir`.

## Claim Boundary

Supported:

- provider-specific known-state execution JSON templates for the Stage 101 calibration gate;
- explicit `|00>`, `|01>`, `|10>`, and `|11>` preparation circuits and expected dominant keys;
- a no-hardware handoff package for collecting calibration evidence without changing the claim boundary.

Excluded:

- real known-state calibration counts;
- completed provider calibration;
- a noisy-hardware robustness result;
- permission to interpret Stage 99 or Stage 100 counts before Stage 101 passes.
