# Q-RoPE Transfer Cascade Reconciliation First Packet v1

## Packet
- Task: `synthetic_symbolic_insufficiency_cascade_reconciliation_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_symbolic_insufficiency_cascade_reconciliation`
  - `V_control_symbolic_symbolic_insufficiency_cascade_reconciliation_regressor`

## Mean Results
- Witness:
  - `mae = 0.082842`
  - `rank_correlation = 0.633333`
  - `calibration_slope = 0.655709`
- Control:
  - `mae = 0.116185`
  - `rank_correlation = 0.035446`
  - `calibration_slope = 0.023604`

## Interpretation
- The declared packet metrics for this line are:
  - `mae`
  - `rank_correlation`
- On both declared packet metrics, the witness led the bounded symbolic control in the mean.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_cascade_reconciliation_v1.csv`
