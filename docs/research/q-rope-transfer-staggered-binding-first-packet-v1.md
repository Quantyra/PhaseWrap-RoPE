# Q-RoPE Transfer Staggered Binding First Packet v1

## Packet
- Task: `synthetic_symbolic_insufficiency_staggered_binding_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_symbolic_insufficiency_staggered_binding`
  - `V_control_symbolic_symbolic_insufficiency_staggered_binding_regressor`

## Mean Results
- Witness:
  - `mae = 0.066442`
  - `rank_correlation = 0.333365`
  - `calibration_slope = 0.586475`
- Control:
  - `mae = 0.096267`
  - `rank_correlation = 0.050416`
  - `calibration_slope = 0.389147`

## Interpretation
- Classification metrics were non-informative for both models on this packet.
- The declared packet metrics for this line are therefore the continuous metrics:
  - `mae`
  - `rank_correlation`
- On both declared packet metrics, the witness led the bounded symbolic control in the mean.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_staggered_binding_v1.csv`
