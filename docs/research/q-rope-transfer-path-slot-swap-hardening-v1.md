# Q-RoPE Transfer Path Slot-Swap Hardening v1

Date: 2026-03-11
Stories: S866

## Packet
- task:
  - `synthetic_symbolic_insufficiency_path_response`
- perturbation:
  - `slot_swap = 1`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`

## Mean Results
- witness:
  - `mae = 0.150405`
  - `rank_correlation = 0.301587`
  - `calibration_slope = 0.418281`
- control:
  - `mae = 0.249839`
  - `rank_correlation = -0.230159`
  - `calibration_slope = -0.426504`

## Interpretation
- the packet was non-inert
- the witness led on both declared metrics in the mean
- the witness also beat the bounded symbolic control on both metrics on seeds `123` and `777`
