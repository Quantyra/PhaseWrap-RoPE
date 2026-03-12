# Q-RoPE Symbolic Insufficiency Dual-Atlas Transition-Quintic-Plus First Packet v1

Date: 2026-03-11
Stories: S840

## Packet
- task: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- models:
  - `V_future_relational_witness_symbolic_insufficiency`
  - `V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quintic_plus`

## Mean Results
- witness:
  - `mae = 0.119724`
  - `rank_correlation = 0.967399`
  - `calibration_slope = 0.989697`
- challenger:
  - `mae = 0.310390`
  - `rank_correlation = 0.168074`
  - `calibration_slope = 0.094748`

## Interpretation
- the challenger did not catch up
- the witness stayed ahead on both declared packet metrics across the fixed three-seed packet
