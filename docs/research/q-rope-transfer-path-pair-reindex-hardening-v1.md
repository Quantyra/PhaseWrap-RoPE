# Q-RoPE Transfer Path Pair-Reindex Hardening v1

Date: 2026-03-11
Stories: S863

## Packet
- task:
  - `synthetic_symbolic_insufficiency_path_response`
- perturbation:
  - `pair_reindex = 1`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- compared:
  - `V_future_relational_witness_symbolic_insufficiency_path`
  - `V_control_symbolic_symbolic_insufficiency_path_regressor`

## Mean Results
- witness:
  - `mae = 0.161655`
  - `rank_correlation = 0.515873`
  - `calibration_slope = 1.112654`
- control:
  - `mae = 0.190125`
  - `rank_correlation = 0.126984`
  - `calibration_slope = 0.377518`

## Interpretation
- the packet was non-inert
- the witness led on both declared metrics in the mean
- the control did not catch up on the fixed structural perturbation
