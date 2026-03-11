# Q-RoPE Symbolic Insufficiency Dual-Atlas Transition-Residual First Packet v1

Date: 2026-03-11
Stories: S760

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
  - `V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_residual`

## Means
- witness:
  - `mae = 0.119724`
  - `rank_correlation = 0.967399`
  - `calibration_slope = 0.989697`
- challenger:
  - `mae = 0.308331`
  - `rank_correlation = 0.174930`
  - `calibration_slope = 0.091783`

## Interpretation
- the transition-residual challenger did not approach the witness on either declared packet metric
- the stronger directional transition-residual layer remained materially weaker than the standing benchmark
