# PhaseWrap-RoPE Stage 4 Real-Hardware Validation Result v1

Date: 2026-05-19

## Result

Stage 4 real-hardware validation has completed on IBM Runtime and Amazon Braket. The current canonical public evidence is the provider-aware hardware sweep manifest at `logs/automated_stage_gates/stage4_hardware_sweep/manifest.json`, verified by `python scripts/verify_stage4_hardware_sweep.py`. The sweep includes IBM Fez and Amazon Braket/Rigetti product-state artifacts plus IBM Fez and Amazon Braket CX artifacts on Rigetti Cepheus, IQM Garnet, and IQM Emerald.

This file is a narrative result note. The manifest and sweep verifier are authoritative when this note and generated JSON artifacts differ in level of detail.

## Current Sweep Summary

| Backend | Provider | Family | Shots | Rows | Witness MAE | Witness rank corr | Control MAE | Control rank corr | Outcome |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| IBM Fez | `ibm_runtime` | `two_qubit_zz_expectation_phase_wrap_v1` | 4096 | 16 | 0.018382 | 0.876558 | 0.217262 | -0.176940 | `hardware-positive` |
| Rigetti Cepheus-1-108Q | `amazon_braket` | `two_qubit_zz_expectation_phase_wrap_v1` | 1000 | 8 | 0.069901 | 0.786644 | 0.149995 | 0.121232 | `hardware-positive` |
| IBM Fez | `ibm_runtime` | `two_qubit_cx_parity_phase_wrap_v2` | 4096 | 16 | 0.021458 | 0.972455 | 0.212516 | -0.169318 | `hardware-positive` |
| Rigetti Cepheus-1-108Q | `amazon_braket` | `two_qubit_cx_parity_phase_wrap_v2` | 1000 | 8 | 0.061643 | 0.557668 | 0.194370 | -0.060616 | `hardware-positive` |
| IQM Garnet | `amazon_braket` | `two_qubit_cx_parity_phase_wrap_v2` | 1000 | 8 | 0.021719 | 0.981981 | 0.204370 | -0.060616 | `hardware-positive` |
| IQM Emerald | `amazon_braket` | `two_qubit_cx_parity_phase_wrap_v2` | 1000 | 8 | 0.021479 | 0.884995 | 0.210995 | -0.096986 | `hardware-positive` |

The Amazon Braket CX records are decoded with manifest-declared `q0q1` bitstring order. The earlier generic `q1q0` classification is retained in the CX portability diagnostic as historical audit context, not as the active scientific classification.

### Amazon Braket / Rigetti Result

- status: `PASS`
- outcome: `hardware-positive`
- provider: `amazon_braket`
- backend: `arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q`
- packet id: `qrope-hardware-5244f90bce2f93b8`
- frozen rows: `8`
- shots per row: `1000`
- hardware tasks: `8`
- task status: all `COMPLETED`
- output bucket: `amazon-braket-us-west-1-485386182336`
- offline verifier result: `pass`

| Variant | MAE | Rank Corr |
| --- | ---: | ---: |
| witness | 0.069901 | 0.786644 |
| control | 0.149995 | 0.121232 |

Gates:

- metadata complete: `true`
- comparability pass: `true`
- hardware direction positive: `true`
- noisy-simulator direction positive: `true`
- direction agreement: `true`
- fail reasons: none

Evidence:

- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z/summary.json`
- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z/frozen_packet.json`
- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z/preflight.json`
- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z/execution.json`
- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z/evaluation.json`
- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z/offline_verification.json`
- `docs/evidence/E002-braket-hardware-runbook.md`

### IBM Runtime Result

Stage 4 real-hardware validation also completed on IBM Runtime and passed the declared deterministic hardware gates.

- status: `PASS`
- outcome: `hardware-positive`
- provider: `ibm_runtime`
- backend: `ibm_fez`
- job id: `d84jbq00bvlc73d4krr0`
- packet id: `qrope-hardware-73c61893576297ff`
- frozen rows: `16`
- shots per row: `4096`
- submitted at UTC: `2026-05-17T03:28:38Z`
- completed at UTC: `2026-05-17T03:29:05Z`
- calibration metadata captured: yes
- backend properties available: yes
- qubits reported: `156`

## IBM Metrics

| Variant | MAE | Rank Corr |
| --- | ---: | ---: |
| witness | 0.018382 | 0.876558 |
| control | 0.217262 | -0.176940 |

## IBM Gates

- metadata complete: `true`
- comparability pass: `true`
- hardware direction positive: `true`
- noisy-simulator direction positive: `true`
- direction agreement: `true`
- fail reasons: none

## IBM Offline Verification

- verifier: `scripts/verify_stage4_hardware_packet.py`
- input packet: `logs/automated_stage_gates/stage4_hardware_packet/frozen_packet.json`
- input execution: `logs/automated_stage_gates/stage4_hardware_packet/execution.json`
- no hardware submission: `true`
- verifier result: `pass`
- output: `logs/automated_stage_gates/stage4_hardware_packet/offline_verification.json`

The default `stage4_hardware_packet/` directory is the single-packet reviewer entry point. The same IBM Fez 2026-05-17 product-state pass is also preserved as immutable named evidence under `logs/automated_stage_gates/stage4_hardware_packet_ibm_fez_20260517_pass/`; the sweep manifest points to that named directory.

## Boundary

These are bounded real-noisy-hardware results for frozen Stage 4 packets on IBM `ibm_fez`, Amazon Braket/Rigetti `Cepheus-1-108Q`, Amazon Braket/IQM `Garnet`, and Amazon Braket/IQM `Emerald`. They support the Stage 4 claim boundary produced by the automated ladder: bounded real-noisy-hardware packets. They do not generalize beyond the frozen packets, backends, dates, calibration windows, provider result-key conventions, and declared metrics. They do not establish quantum advantage, production transformer superiority, full transformer-scale validation, or general cross-backend robustness.

## Evidence

- `logs/automated_stage_gates/stage4_hardware_packet/summary.json`
- `logs/automated_stage_gates/stage4_hardware_packet/frozen_packet.json`
- `logs/automated_stage_gates/stage4_hardware_packet/preflight.json`
- `logs/automated_stage_gates/stage4_hardware_packet/execution.json`
- `logs/automated_stage_gates/stage4_hardware_packet/evaluation.json`
- `logs/automated_stage_gates/stage4_hardware_sweep/manifest.json`
- `logs/automated_stage_gates/stage4_hardware_sweep/offline_verification.json`
- `docs/research/q-rope-stage4-hardware-packet-v1.md`
