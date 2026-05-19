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
| `two_qubit_cx_parity_phase_wrap_v2` | Implemented; no-hardware ideal-count rehearsal passes; deferred from the active public hardware sweep | Entangling CX witness variant. Hardware evidence requires a future dated run with committed raw counts, metadata, and verifier output. |

## No-hardware CX rehearsal

The CX lane has a local ideal-count rehearsal artifact:

- artifact directory: `logs/automated_stage_gates/stage4_cx_rehearsal/ideal_counts_rehearsal/`
- command: `python scripts/prepare_stage4_cx_rehearsal.py`
- family: `two_qubit_cx_parity_phase_wrap_v2`
- rows: `16`
- shots: `4096`
- witness MAE: `0.000051`
- witness rank correlation: `1.000000`
- control MAE: `0.229743`
- control rank correlation: `-0.171995`
- gate pass: `true`

This rehearsal uses deterministic ideal counts and submits no hardware job. It is readiness evidence for the packet/evaluation mechanics only, not Stage 4 hardware evidence.

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

Current provider posture (2026-05-19): IBM Fez and Amazon Braket/Rigetti have active Stage 4 evidence paths in this repository. The Braket/Rigetti product-state artifact is present and machine-verifiable. Additional IBM backends and the CX hardware lane are deferred from the active public sweep unless real per-backend/per-family raw-count artifacts are added. The CX lane is ready for credentialled execution in the narrow sense that the no-hardware ideal-count rehearsal passes; an Amazon Braket/Rigetti CX hardware attempt was submitted on 2026-05-19 but timed out while queued, cancellation was requested, and no raw counts were produced. IonQ is excluded from the active sweep: the current intended IonQ route is Amazon Braket, but the checked Braket IonQ devices were unavailable on 2026-05-19: `Forte-1` and `Forte-Enterprise-1` were `OFFLINE`, and `Aria-1` was `RETIRED`; no IonQ hardware task was submitted. Quandela Stage 4 execution remains configured to simulator profiles unless explicitly changed.

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
