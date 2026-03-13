# Q-RoPE Transfer Cascade Reconciliation Pair-Reindex Hardening v1

## Fixed Hardening Packet
- Task: `synthetic_symbolic_insufficiency_cascade_reconciliation_response`
- Perturbation: `pair_reindex=1`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_symbolic_insufficiency_cascade_reconciliation`
  - `V_control_symbolic_symbolic_insufficiency_cascade_reconciliation_regressor`

## Mean Results
- Witness:
  - `mae = 0.094736`
  - `rank_correlation = 0.633334`
  - `calibration_slope = 1.200674`
- Control:
  - `mae = 0.140556`
  - `rank_correlation = 0.161407`
  - `calibration_slope = 0.628408`

## Interpretation
- `pair_reindex=1` was non-inert.
- The witness stayed ahead of the bounded symbolic control on both declared packet metrics in the mean.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_cascade_reconciliation_pair1_v1.csv`
