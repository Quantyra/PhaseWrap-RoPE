# PhaseWrap-RoPE replication ledger v1

Status: `CREDENTIALLED_HARDWARE_EXECUTION_REQUIRED`

Date: `2026-05-18`

## Purpose

This ledger records what has actually been executed and what remains blocked. It is intentionally separate from the replication plan so reviewers can distinguish completed evidence from intended replication work.

Machine-readable ledger: `logs/automated_stage_gates/replication_lanes/replication-ledger.json`

## Current execution state

| Lane | Circuit family | Target | Status | Public evidence claim |
| --- | --- | --- | --- | --- |
| Stage 4 product original | `two_qubit_zz_expectation_phase_wrap_v1` | IBM `ibm_fez`, `2026-05-17` | `published_completed` | Bounded hardware-positive result for one packet/backend/date/calibration context. |
| Product rerun A | `two_qubit_zz_expectation_phase_wrap_v1` | Second IBM backend, date 1 | `blocked_pending_credentials_and_backend_selection` | No replication claim. |
| Product rerun B | `two_qubit_zz_expectation_phase_wrap_v1` | Third IBM backend or same backend on date 2 | `blocked_pending_credentials_and_backend_selection` | No replication claim. |
| CX rerun A | `two_qubit_cx_parity_phase_wrap_v2` | IBM backend with acceptable CX profile, date 1 | `implemented_not_executed_on_hardware` | No entangling-witness evidence claim. |
| CX rerun B | `two_qubit_cx_parity_phase_wrap_v2` | Second date or second backend | `implemented_not_executed_on_hardware` | No entangling-witness evidence claim. |

## Local preflight result for this update

The implementation environment had IBM/Qiskit runtime dependencies available, but no IBM Quantum token, backend, or budget-cap environment variables were configured. That means the repo can prepare and document the replication lanes, but it cannot honestly publish new hardware execution results from this environment.

This is a blocker, not a failure of the method. A replication lane becomes publishable only after it contains:

- completed raw counts;
- backend metadata;
- calibration metadata;
- job identifier retained in the evidence record;
- verifier output recomputed from the published packet files.

## Publication rule

Do not describe PhaseWrap-RoPE as cross-backend robust, cross-date replicated, or entanglement-validated until the relevant lane changes from blocked/planned to completed with raw counts and verifier output. Negative or inconclusive replications should be published in this ledger rather than hidden.
