# Q-RoPE Transfer Braid Slot-Swap Hardening v1

Date: 2026-03-12
Stories: S950

## Fixed Packet
- task: `synthetic_symbolic_insufficiency_braid_crossing_response`
- perturbation: `slot_swap = 1`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- retained models:
  - `V_future_relational_witness_symbolic_insufficiency_braid`
  - `V_control_symbolic_symbolic_insufficiency_braid_regressor`

## Mean Results
- witness:
  - `mae = 0.094523`
  - `rank_correlation = 0.560277`
  - `calibration_slope = 0.993025`
- control:
  - `mae = 0.125137`
  - `rank_correlation = 0.064220`
  - `calibration_slope = 0.072686`

## Interpretation
- the perturbation was non-inert
- the witness still beat the bounded symbolic control on both declared packet metrics in the mean
- this keeps the braid branch active and justifies deeper structural hardening next
