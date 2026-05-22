# PhaseWrap-RoPE Stage 100 Matched CX Encoding Packet Freezer v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 100 resolves the Stage 99 open question about whether the noisy-hardware protocol should include a matched entangling witness path.

Decision: include it.

Reason: Stage 4 contains both product-state and CX/parity hardware-positive lanes. If future noisy-hardware comparison only used the Stage 99 product-state packets, the study would not cover the existing entangling witness surface. Stage 100 therefore freezes matched CX/parity packets before hardware execution.

## Reviewer Command

```bash
python scripts/run_stage100_matched_cx_encoding_packet_freezer.py
```

This writes:

- `logs/automated_stage_gates/stage100_matched_cx_encoding_packets/manifest.json`
- `logs/automated_stage_gates/stage100_matched_cx_encoding_packets/results.json`
- `logs/automated_stage_gates/stage100_matched_cx_encoding_packets/summary.csv`
- `logs/automated_stage_gates/stage100_matched_cx_encoding_packets/packets/*.json`

## Result

Stage 100 records `MATCHED_CX_ENCODING_PACKETS_FROZEN_NO_HARDWARE`.

Frozen encoding families:

- `phasewrap`
- `rope_like`
- `sinusoidal_like`
- `alibi_like`
- `no_position_control`

Frozen CX source lanes:

- `ibm_cx_seed314_rows16_shots4096`
- `braket_cx_seed2718_rows8_shots1000`

The packet freezer preserves the source row sets from the Stage 4 preregistered CX lanes and emits one matched packet per lane per encoding family.

## Fixed-Width Template

All Stage 100 packets use:

- measured qubits: `2`
- active qubits: `2`
- readout: `computational_basis`
- circuit template: `two_ry_cx_parity_z_readout_v1`
- entangling gate: `cx q0->q1`
- score observable: `0.5 + 0.25 * (E[Z0 after CX] + E[Z0 Z1 after CX])`

The template maps each encoding to two bounded components, prepares them with two `RY` rotations, applies a single CNOT, and reads the components back through a parity observable. Under ideal CNOT readout, `E[Z0 after CX]` recovers the first component and `E[Z0 Z1 after CX]` recovers the second component.

## Interpretation

Stage 100 is still a setup result, not a hardware result.

Together, Stage 99 and Stage 100 now freeze matched product-state and CX/parity packet families for the noisy-hardware comparison. The next hard prerequisite is provider/backend/date bitstring calibration using known-state counts.

## Claim Boundary

Supported:

- matched no-hardware packet freeze for five two-qubit CX/parity positional-score encoding families;
- identical CX-lane row sets across PhaseWrap, RoPE-like, sinusoidal-like, ALIBI-like, and no-position/control encodings;
- a fixed-width entangling score readout template paired with the Stage 99 product-state packet family.

Excluded:

- a noisy-hardware robustness result;
- a claim that PhaseWrap-RoPE outperforms RoPE on hardware;
- a transformer-performance claim;
- provider bitstring-order validation;
- independent backend/date/calibration robustness.

## Remaining Requirements

- Run known-state bitstring calibration counts per provider/backend/date.
- Execute Stage 99 product-state and Stage 100 CX/parity matched packets under fixed shot budgets only after calibration evidence is present.
- Compare readout error, rank retention, score distortion, and auditability metrics against the no-position/control family.
- Repeat selected packets across independent backend calibration windows before claiming robustness beyond recorded contexts.
