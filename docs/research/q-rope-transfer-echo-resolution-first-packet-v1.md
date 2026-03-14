# Q-RoPE Transfer Echo-Resolution First Packet v1

## Packet
- Task: `synthetic_symbolic_insufficiency_echo_resolution_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_symbolic_insufficiency_echo_resolution`
  - `V_control_symbolic_symbolic_insufficiency_echo_resolution_regressor`

## Mean Results
- Witness:
  - `mae = 0.096616`
  - `rank_correlation = 0.332497`
  - `calibration_slope = 0.272135`
- Control:
  - `mae = 0.107773`
  - `rank_correlation = -0.055800`
  - `calibration_slope = -0.274371`

## Interpretation
- The declared packet metrics for this line are:
  - `mae`
  - `rank_correlation`
- On both declared packet metrics, the witness led the bounded symbolic control in the mean.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_echo_resolution_v1.csv`
