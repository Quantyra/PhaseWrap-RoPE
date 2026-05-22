# QRoPE Stage 150 - First Provider Result Lineage Audit

## Objective
Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, under fixed circuit width.

## Result
Stage 150 audits IBM Runtime first-provider result lineage before live execution. It does not submit hardware jobs, create live provider SDK clients, record credentials, or write real provider result records.

Current decision: `FIRST_PROVIDER_RESULT_LINEAGE_CONTRACT_READY_EXECUTION_BLOCKED`.

The lineage contract verifies that expected IBM Runtime jobs are traceable across:

- Stage 112 provider execution jobs
- Stage 114 provider/window job shards and required result fields
- Stage 107 window target evidence paths
- Stage 148 statistical interpretation windows
- Stage 149 guarded runner contract readiness

It also records the backend metadata fields required on later real provider result records:

- `provider`
- `backend`
- `window_id`
- `job_kind`

## Claim Boundary
Supported:

- first-provider job lineage from Stage 112 jobs to Stage 114 shards, result fields, and Stage 107 target evidence paths
- window-level IBM calibration and matched-packet job completeness before provider result interpretation
- binding of expected result lineage to Stage 148 statistical interpretation and Stage 149 guarded runner checks

Excluded:

- provider credential values
- hardware job submission
- live provider SDK client creation
- real provider result records
- a noisy-hardware robustness or auditability conclusion

## Evidence
- `logs/automated_stage_gates/stage150_first_provider_result_lineage_audit/manifest.json`
- `logs/automated_stage_gates/stage150_first_provider_result_lineage_audit/results.json`
- `logs/automated_stage_gates/stage150_first_provider_result_lineage_audit/summary.csv`
