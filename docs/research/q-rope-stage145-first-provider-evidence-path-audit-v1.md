# QRoPE Stage 145 - First Provider Evidence Path Audit

## Objective
Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, under fixed circuit width.

## Result
Stage 145 audits the IBM-first evidence path that follows authorized provider execution. It also adds provider-scoped options to the non-submitting collection and evaluation entrypoints so the IBM Runtime windows can be collected and evaluated without requiring Amazon Braket result shards first.

Current decision: `FIRST_PROVIDER_EVIDENCE_PATH_PREPARED_RESULTS_BLOCKED`.

The first blocked readiness record is `post_configuration_authorized_runner_chain`, because Stage 144 still blocks at Stage 140 local IBM Runtime configuration.

The first-provider evidence path currently expects 328 IBM Runtime job results across two result shards, with 0 result records present.

## Provider-Scoped Commands
```powershell
python scripts/run_stage115_provider_result_collector.py --provider ibm_runtime --write-stage113-input
python scripts/run_stage113_job_result_evidence_assembler.py --provider ibm_runtime --write-evidence
python scripts/run_stage109_window_evidence_intake_validator.py --provider ibm_runtime
python scripts/run_stage137_auditability_metric_evaluator.py --provider ibm_runtime
python scripts/run_stage110_replicated_advantage_claim_gate.py
python scripts/run_stage138_objective_claim_gate.py
```

## Claim Boundary
Supported:

- first-provider evidence intake readiness after authorized IBM Runtime execution
- Stage 144 ready-transition and authorized-runner count enforcement before provider result collection
- provider-scoped Stage 115, Stage 113, Stage 109, and Stage 137 command sequence
- explicit blocker reporting before Stage 138 objective wording

Excluded:

- provider credential values
- hardware job submission
- live provider SDK client creation
- real provider result records
- a noisy-hardware robustness or auditability conclusion

## Evidence
- `logs/automated_stage_gates/stage145_first_provider_evidence_path_audit/manifest.json`
- `logs/automated_stage_gates/stage145_first_provider_evidence_path_audit/results.json`
- `logs/automated_stage_gates/stage145_first_provider_evidence_path_audit/summary.csv`
