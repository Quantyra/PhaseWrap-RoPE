# Q-RoPE Symbolic Insufficiency Dual-Atlas Bilinear Residual First Packet v1

Date: 2026-03-11
Stories: S750

## Packet
- task: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds:
  - `42`
  - `123`
  - `777`
- witness:
  - `V_future_relational_witness_symbolic_insufficiency`
- challenger:
  - `V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_bilinear`

## Means
- witness:
  - `mae = 0.119724`
  - `rank_correlation = 0.967399`
  - `calibration_slope = 0.989697`
- challenger:
  - `mae = 0.299048`
  - `rank_correlation = 0.176899`
  - `calibration_slope = 0.112911`

## Interpretation
- the bilinear residual challenger did not approach the witness on either declared packet metric
- the stronger bilinear layer remained materially weaker than the standing benchmark
