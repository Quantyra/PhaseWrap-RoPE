# PhaseWrap-RoPE Stage 101 Known-State Calibration Gate v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 101 makes the next noisy-hardware prerequisite explicit and executable: known-state bitstring calibration must pass before Stage 99 or Stage 100 hardware counts can be interpreted.

Stage 99 froze matched product-state packets. Stage 100 froze matched CX/parity packets. Both depend on provider/backend/date-specific decoding of two measured qubits. Stage 101 therefore blocks hardware interpretation until raw counts for `|00>`, `|01>`, `|10>`, and `|11>` are supplied and verify a bitstring order with a declared dominant-count threshold.

## Reviewer Command

```bash
python scripts/run_stage101_known_state_calibration_gate.py
```

This writes:

- `logs/automated_stage_gates/stage101_known_state_calibration_gate/manifest.json`
- `logs/automated_stage_gates/stage101_known_state_calibration_gate/results.json`
- `logs/automated_stage_gates/stage101_known_state_calibration_gate/summary.csv`

To verify real calibration evidence later, provide execution files named:

- `ibm_runtime_known_state_execution.json`
- `amazon_braket_known_state_execution.json`

and run:

```bash
python scripts/run_stage101_known_state_calibration_gate.py --execution-dir PATH_TO_EXECUTION_DIR
```

Each execution file must include `job_or_task_ids`, `backend_metadata`, `submitted_at_utc`, `completed_at_utc`, and `raw_counts_by_state`.

## Result

Current decision:

`KNOWN_STATE_CALIBRATION_COUNTS_REQUIRED_BEFORE_HARDWARE_INTERPRETATION`

This is expected. The repo has no real known-state execution counts yet. Stage 101 confirms that the Stage 99 and Stage 100 packet surfaces are frozen, but it still blocks interpretation of future noisy-hardware packets until provider/backend/date-specific known-state calibration passes.

## Calibration Rule

Stage 101 checks both candidate bitstring orders:

- `q0q1`
- `q1q0`

For each prepared state, the dominant measured key must match the expected key for exactly one order. The default minimum dominant fraction is `0.80`.

## Claim Boundary

Supported:

- an executable known-state calibration evidence gate for Stage 99 and Stage 100 matched packet interpretation;
- explicit bitstring-order inference over `|00>`, `|01>`, `|10>`, and `|11>` raw counts;
- a hard block against interpreting matched hardware packets before calibration evidence passes.

Excluded:

- completed provider calibration without raw known-state counts;
- a noisy-hardware robustness result;
- a provider-wide bitstring-order claim beyond the recorded backend/date/calibration metadata.

## Next Gate

Supply real known-state execution JSON per provider/backend/date, then rerun Stage 101 before executing or interpreting Stage 99 and Stage 100 matched packets.
