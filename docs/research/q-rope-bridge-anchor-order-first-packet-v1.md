# Q-RoPE Bridge Anchor-Order First Packet v1

## Packet
- Task: `synthetic_positional_anchor_order_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_positional_anchor_order`
  - `V_control_symbolic_positional_anchor_order_regressor`

## Mean Results
- Witness:
  - `mae = 0.104561`
  - `rank_correlation = 0.123543`
  - `calibration_slope = 0.231696`
- Control:
  - `mae = 0.117350`
  - `rank_correlation = -0.403263`
  - `calibration_slope = -1.163783`

## Interpretation
- The declared packet metrics for this line are:
  - `mae`
  - `rank_correlation`
- On both declared packet metrics, the witness led the bounded symbolic control in the mean.
- The bridge-task line stays active and advances to the fixed `token_permutation=cdab` nuisance hardening step.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/bridge_anchor_order_v1.csv`
