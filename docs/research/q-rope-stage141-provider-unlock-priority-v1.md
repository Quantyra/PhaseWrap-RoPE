# QRoPE Stage 141 - Provider Unlock Priority

## Objective
Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, under fixed circuit width.

## Result
Stage 141 prioritizes the first provider unlock path using non-secret Stage 139 and Stage 140 evidence.

Current decision: `PROVIDER_UNLOCK_PRIORITY_PREPARED_EXECUTION_BLOCKED`.

Current first unlock provider: `ibm_runtime`, because the IBM SDK modules are present and the remaining local blocker is the `IBM_QUANTUM_INSTANCE_CRN` environment/configuration group. Amazon Braket remains behind missing SDK modules plus missing local configuration groups.

## Claim Boundary
Supported:

- provider unlock ordering based on non-secret env-key and SDK readiness evidence
- top-level first-provider missing env groups, missing SDK modules, and minimal unlock actions
- minimal first-provider unlock actions before Stage 106/111/129 reruns
- explicit separation from live provider submission and Stage 138 objective claims

Excluded:

- provider credential values
- hardware job submission
- live provider SDK client creation
- real provider result records
- a noisy-hardware robustness or auditability conclusion

## Evidence
- `logs/automated_stage_gates/stage141_provider_unlock_priority/manifest.json`
- `logs/automated_stage_gates/stage141_provider_unlock_priority/results.json`
- `logs/automated_stage_gates/stage141_provider_unlock_priority/summary.csv`
