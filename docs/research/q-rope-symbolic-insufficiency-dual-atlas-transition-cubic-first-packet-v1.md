# Q-RoPE Symbolic-Insufficiency Dual-Atlas Transition-Cubic First Packet v1

Date: 2026-03-11
Status: done
Stories: S790

## Fixed Packet
- task: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- witness: `V_future_relational_witness_symbolic_insufficiency`
- challenger: `V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_cubic`

## Mean Results
- witness:
  - `mae = 0.119724`
  - `rank_correlation = 0.967399`
  - `calibration_slope = 0.989697`
- challenger:
  - `mae = 0.310598`
  - `rank_correlation = 0.173982`
  - `calibration_slope = 0.088766`

## Outcome
- the witness stayed ahead on both declared packet metrics across all three seeds
