# PhaseWrap-RoPE Stage 4 Bitstring Calibration Plan v1

Date: `2026-05-20`

## Purpose

This no-hardware artifact predeclares known-state calibration packets for provider bitstring-order validation. It addresses the Braket CX lesson directly: provider result-key conventions can change the interpretation of small two-qubit witness records, so future provider-level claims require explicit `|00>`, `|01>`, `|10>`, and `|11>` calibration counts.

Artifacts:

- Manifest: `logs/automated_stage_gates/stage4_bitstring_calibration/manifest.json`
- Offline verifier output: `logs/automated_stage_gates/stage4_bitstring_calibration/offline_verification.json`
- IBM packet spec: `logs/automated_stage_gates/stage4_bitstring_calibration/ibm_runtime_known_state_packet.json`
- Amazon Braket packet spec: `logs/automated_stage_gates/stage4_bitstring_calibration/amazon_braket_known_state_packet.json`
- Preparation script: `scripts/prepare_stage4_bitstring_calibration_packets.py`
- Verifier: `scripts/verify_stage4_bitstring_calibration.py`

Prepare packet specs:

```bash
python scripts/prepare_stage4_bitstring_calibration_packets.py
```

Verify supplied calibration artifacts:

```bash
python scripts/verify_stage4_bitstring_calibration.py
```

The default verifier currently fails with `missing-evidence` because no real known-state calibration counts have been supplied. That is intentional.

## Claim Boundary

This artifact is a calibration plan and verifier contract, not completed provider calibration and not new hardware evidence. A future completed calibration record must add real raw counts, task or job IDs, backend metadata, submitted/completed timestamps, and offline verifier output before any broader provider bitstring-order statement is promoted.
