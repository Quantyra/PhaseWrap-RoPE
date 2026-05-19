# QRoPE replication plan v1

Status: `READY_FOR_CREDENTIALLED_EXECUTION`

Date: `2026-05-18`

## Purpose

This plan separates saved-count recomputation from independent replication.

- Recompute: run the verifier against already-published raw counts.
- Replicate: submit a new hardware job for the same frozen packet family, capture new raw counts and metadata, and compare metrics.

## Implemented witness families

| Circuit family | Status | Claim boundary |
| --- | --- | --- |
| `two_qubit_zz_expectation_phase_wrap_v1` | Executed once on `ibm_fez` | Product-state angle-encoding/readout witness. |
| `two_qubit_cx_parity_phase_wrap_v2` | Executed across IBM `ibm_kingston`, `ibm_marrakesh`, `ibm_fez`, and IonQ `ionq_qpu` | Entangling CX witness variant. Hardware evidence recorded in the comparison report. |

## Minimum replication matrix

| Lane | Circuit family | Backend/date target | Required status before promotion |
| --- | --- | --- | --- |
| Product-state rerun A | `two_qubit_zz_expectation_phase_wrap_v1` | second IBM backend, date 1 | Completed raw counts, metadata, verifier pass/fail recorded. |
| Product-state rerun B | `two_qubit_zz_expectation_phase_wrap_v1` | third IBM backend or same backend on date 2 | Completed raw counts, metadata, verifier pass/fail recorded. |
| Entangling rerun A | `two_qubit_cx_parity_phase_wrap_v2` | IBM backend with acceptable CX error profile, date 1 | Completed raw counts, metadata, verifier pass/fail recorded. |
| Entangling rerun B | `two_qubit_cx_parity_phase_wrap_v2` | second date or second backend | Completed raw counts, metadata, verifier pass/fail recorded. |

## Execution prerequisites

- IBM Quantum credentials available through `IBM_QUANTUM_TOKEN` or `QISKIT_IBM_TOKEN`.
- Optional IBM Cloud instance CRN through `IBM_QUANTUM_INSTANCE_CRN`.
- Runtime dependencies installed:

Current provider posture (2026-05-19): only IBM hardware backends are used for Stage 4 replication runs. `ionq_qpu` and `ionq` `QPU Targets` are not currently enabled, and Quandela Stage 4 execution remains configured to simulator profiles unless explicitly changed.

```bash
python -m pip install -e ".[ibm]"
```

## Product-state replication command

PowerShell:

```powershell
$env:QROPE_REAL_HARDWARE_PROVIDER = "ibm_runtime"
$env:QROPE_HARDWARE_BACKEND = "<backend-name>"
$env:QROPE_HARDWARE_CIRCUIT_FAMILY = "two_qubit_zz_expectation_phase_wrap_v1"
$env:QROPE_HARDWARE_ROW_LIMIT = "16"
$env:QROPE_HARDWARE_SHOT_COUNT = "4096"
$env:QROPE_HARDWARE_BUDGET_USD_CAP = "<approved-budget>"
python scripts/run_automated_stage_gates.py
python scripts/verify_stage4_hardware_packet.py --expected-backend "<backend-name>" --expected-job-id "<job-id>"
```

Bash:

```bash
export QROPE_REAL_HARDWARE_PROVIDER="ibm_runtime"
export QROPE_HARDWARE_BACKEND="<backend-name>"
export QROPE_HARDWARE_CIRCUIT_FAMILY="two_qubit_zz_expectation_phase_wrap_v1"
export QROPE_HARDWARE_ROW_LIMIT="16"
export QROPE_HARDWARE_SHOT_COUNT="4096"
export QROPE_HARDWARE_BUDGET_USD_CAP="<approved-budget>"
python scripts/run_automated_stage_gates.py
python scripts/verify_stage4_hardware_packet.py --expected-backend "<backend-name>" --expected-job-id "<job-id>"
```

## Entangling CX replication command

PowerShell:

```powershell
$env:QROPE_REAL_HARDWARE_PROVIDER = "ibm_runtime"
$env:QROPE_HARDWARE_BACKEND = "<backend-name>"
$env:QROPE_HARDWARE_CIRCUIT_FAMILY = "two_qubit_cx_parity_phase_wrap_v2"
$env:QROPE_HARDWARE_ROW_LIMIT = "16"
$env:QROPE_HARDWARE_SHOT_COUNT = "4096"
$env:QROPE_HARDWARE_BUDGET_USD_CAP = "<approved-budget>"
python scripts/run_automated_stage_gates.py
python scripts/verify_stage4_hardware_packet.py --expected-backend "<backend-name>" --expected-job-id "<job-id>"
```

Bash:

```bash
export QROPE_REAL_HARDWARE_PROVIDER="ibm_runtime"
export QROPE_HARDWARE_BACKEND="<backend-name>"
export QROPE_HARDWARE_CIRCUIT_FAMILY="two_qubit_cx_parity_phase_wrap_v2"
export QROPE_HARDWARE_ROW_LIMIT="16"
export QROPE_HARDWARE_SHOT_COUNT="4096"
export QROPE_HARDWARE_BUDGET_USD_CAP="<approved-budget>"
python scripts/run_automated_stage_gates.py
python scripts/verify_stage4_hardware_packet.py --expected-backend "<backend-name>" --expected-job-id "<job-id>"
```

## Publication rule

Do not broaden the QRoPE claim boundary until at least one replication lane produces completed raw counts, metadata, and verifier output. Negative or inconclusive replications should be published as evidence rather than hidden.

Completed comparison report:

- `docs/research/q-rope-stage4-hardware-comparison-v1.md`
