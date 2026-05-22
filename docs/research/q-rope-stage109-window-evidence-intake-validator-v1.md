# QRoPE Stage 109 Window Evidence Intake Validator

Stage 109 adds a no-submission evidence intake gate for the noisy-hardware robustness lane. It validates whether each Stage 107 independent execution window has enough completed evidence to support Stage 103 metric interpretation and later Stage 105 aggregation.

The validator reads `logs/automated_stage_gates/stage107_window_execution_orchestrator/window_execution_plans.json` and checks each planned window for:

- the filled known-state calibration execution JSON;
- Stage 113 assembly status on calibration and packet evidence files;
- Stage 113 live-submit provenance showing Stage 115/152 write readiness, all-command authorization, and all-command live-submit readiness;
- Stage 101 results showing `known_state_calibration_pass: true` and the ready decision;
- one packet execution JSON per Stage 107 packet template;
- non-empty `job_or_task_ids`, `backend_metadata`, `submitted_at_utc`, `completed_at_utc`, and `raw_counts_by_row` fields for each packet execution;
- non-empty counts for every expected packet row;
- Stage 103 results showing `ready_to_interpret_hardware_metrics: true`.

The gate deliberately does not submit hardware jobs, validate credentials, or infer a PhaseWrap-RoPE advantage. It only records whether evidence is complete enough for the next aggregation step.

Current expected decision before real provider execution:

`WINDOW_EVIDENCE_INTAKE_BLOCKED_EVIDENCE_MISSING`

Readiness decision after all windows are filled and verified:

`WINDOW_EVIDENCE_INTAKE_READY_FOR_STAGE105_AGGREGATION`
