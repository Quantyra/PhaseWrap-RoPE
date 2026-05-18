# Q-RoPE Stage 4 Real-Hardware Validation Result v1

Date: 2026-05-16

## Result

Stage 4 real-hardware validation completed on IBM Runtime and passed the declared deterministic hardware gates.

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

## Metrics

| Variant | MAE | Rank Corr |
| --- | ---: | ---: |
| witness | 0.018382 | 0.876558 |
| control | 0.217262 | -0.176940 |

## Gates

- metadata complete: `true`
- comparability pass: `true`
- hardware direction positive: `true`
- noisy-simulator direction positive: `true`
- direction agreement: `true`
- fail reasons: none

## Offline Verification

- verifier: `scripts/verify_stage4_hardware_packet.py`
- input packet: `logs/automated_stage_gates/stage4_hardware_packet/frozen_packet.json`
- input execution: `logs/automated_stage_gates/stage4_hardware_packet/execution.json`
- no hardware submission: `true`
- verifier result: `pass`
- output: `logs/automated_stage_gates/stage4_hardware_packet/offline_verification.json`

## Boundary

This is a bounded real-noisy-hardware result for the frozen 16-row Stage 4 packet on IBM `ibm_fez`. It supports the Stage 4 claim boundary produced by the automated ladder: bounded real-noisy-hardware packet. It does not generalize beyond the frozen packet, backend, date, calibration window, and declared metrics.

## Evidence

- `logs/automated_stage_gates/stage4_hardware_packet/summary.json`
- `logs/automated_stage_gates/stage4_hardware_packet/frozen_packet.json`
- `logs/automated_stage_gates/stage4_hardware_packet/preflight.json`
- `logs/automated_stage_gates/stage4_hardware_packet/execution.json`
- `logs/automated_stage_gates/stage4_hardware_packet/evaluation.json`
- `docs/research/q-rope-stage4-hardware-packet-v1.md`
