# PhaseWrap-RoPE Stage 99 Matched Fixed-Width Encoding Packet Freezer v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 99 closes the first missing protocol gate from Stage 98 by freezing matched no-hardware packet specs for a future noisy-hardware comparison.

Goal:

> Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, under fixed circuit width.

Stage 99 does not run hardware. It defines the matched packet surface that must exist before hardware execution can be treated as a fair PhaseWrap-vs-comparator robustness test.

## Reviewer Command

```bash
python scripts/run_stage99_matched_fixed_width_encoding_packet_freezer.py
```

This writes:

- `logs/automated_stage_gates/stage99_matched_fixed_width_encoding_packets/manifest.json`
- `logs/automated_stage_gates/stage99_matched_fixed_width_encoding_packets/results.json`
- `logs/automated_stage_gates/stage99_matched_fixed_width_encoding_packets/summary.csv`
- `logs/automated_stage_gates/stage99_matched_fixed_width_encoding_packets/packets/*.json`

## Result

Stage 99 records `MATCHED_FIXED_WIDTH_ENCODING_PACKETS_FROZEN_NO_HARDWARE`.

Frozen encoding families:

- `phasewrap`
- `rope_like`
- `sinusoidal_like`
- `alibi_like`
- `no_position_control`

Frozen source lanes:

- `ibm_product_seed314_rows16_shots4096`
- `braket_product_seed2718_rows8_shots1000`

The packet freezer preserves the source row sets from the Stage 4 preregistered product-state lanes and emits one matched packet per lane per encoding family.

## Fixed-Width Template

All Stage 99 packets use:

- measured qubits: `2`
- active qubits: `2`
- readout: `computational_basis`
- circuit template: `two_ry_product_state_z_readout_v1`
- score observable: `0.5 + 0.25 * (E[Z0] + E[Z1])`

The template maps each encoding to two bounded components and converts those components into two `RY` product-state preparation angles. This makes the future comparison row-matched, width-matched, and readout-matched.

## Interpretation

Stage 99 is a setup result, not a hardware result.

It supports the claim that the noisy-hardware track now has frozen matched fixed-width product-state packet specs for PhaseWrap, RoPE-like, sinusoidal-like, ALIBI-like, and no-position/control families.

It does not support a claim that PhaseWrap-RoPE is more robust on hardware. That requires executing these packets after known-state bitstring calibration and then comparing measured readout stability under the declared fixed-width protocol.

## Claim Boundary

Supported:

- matched no-hardware packet freeze for five two-qubit positional-score encoding families;
- identical row sets within each source lane across PhaseWrap, RoPE-like, sinusoidal-like, ALIBI-like, and no-position/control encodings;
- a fixed-width product-state score readout template for future noisy-hardware execution planning.

Excluded:

- a noisy-hardware robustness result;
- a claim that PhaseWrap-RoPE outperforms RoPE on hardware;
- a transformer-performance claim;
- provider bitstring-order validation;
- independent backend/date/calibration robustness.

## Remaining Requirements

- Review whether the product-state template is sufficient or whether a matched CX witness variant is also required.
- Run known-state bitstring calibration counts per provider/backend/date.
- Execute matched packets under fixed shot budgets only after calibration evidence is present.
- Repeat selected packets across independent backend calibration windows before claiming robustness beyond recorded contexts.
