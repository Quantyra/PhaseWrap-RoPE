# QRoPE Stage 149 - First Provider Guarded Runner Contract Audit

## Objective
Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, under fixed circuit width.

## Result
Stage 149 audits the IBM Runtime guarded runner contract with synthetic injected submitters. It does not submit hardware jobs, create live provider SDK clients, record credentials, or write real provider result records.

Current decision: `FIRST_PROVIDER_GUARDED_RUNNER_CONTRACT_READY_CUTOVER_BLOCKED`.

The synthetic contract checks verify:

- a valid injected submitter writes a Stage 114-shaped provider result JSONL record
- Stage 129 cutover authorization is required before any guarded result write
- invalid submitter records are rejected without writing provider result files

Current real-path status remains blocked:

- `current_stage111_ready=false`
- `current_stage129_cutover_authorized=false`
- `first_provider_authorized_runner_count=0`

## Claim Boundary
Supported:

- IBM guarded runner validates Stage 114-shaped result records before writing provider result JSONL
- Stage 129 cutover authorization is required before any guarded result write
- invalid submitter records fail closed without writing provider result files

Excluded:

- provider credential values
- hardware job submission
- live provider SDK client creation
- real provider result records
- a noisy-hardware robustness or auditability conclusion

## Evidence
- `logs/automated_stage_gates/stage149_first_provider_guarded_runner_contract_audit/manifest.json`
- `logs/automated_stage_gates/stage149_first_provider_guarded_runner_contract_audit/results.json`
- `logs/automated_stage_gates/stage149_first_provider_guarded_runner_contract_audit/summary.csv`
