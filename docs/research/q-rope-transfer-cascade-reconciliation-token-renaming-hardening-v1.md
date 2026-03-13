# Q-RoPE Transfer Cascade Reconciliation Token Renaming Hardening v1

## Fixed Hardening Packet
- Task: `synthetic_symbolic_insufficiency_cascade_reconciliation_response`
- Perturbation: `token_permutation=cdab`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_symbolic_insufficiency_cascade_reconciliation`
  - `V_control_symbolic_symbolic_insufficiency_cascade_reconciliation_regressor`

## Mean Results
- Witness:
  - `mae = 0.103797`
  - `rank_correlation = 0.342157`
  - `calibration_slope = 0.488318`
- Control:
  - `mae = 0.151390`
  - `rank_correlation = -0.141176`
  - `calibration_slope = -0.181584`

## Interpretation
- `token_permutation=cdab` was non-inert.
- The witness stayed ahead of the bounded symbolic control on both declared packet metrics in the mean.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_cascade_reconciliation_cdab_v1.csv`
