# Q-RoPE Bridge Anchor-Distance First Packet v1

## Packet
- Task: `synthetic_positional_anchor_distance_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_positional_anchor_distance`
  - `V_control_symbolic_positional_anchor_distance_regressor`

## Mean Results
- Witness:
  - `mae = 0.164006`
  - `rank_correlation = -0.266667`
  - `calibration_slope = -0.361534`
- Control:
  - `mae = 0.207028`
  - `rank_correlation = -0.933333`
  - `calibration_slope = -0.662443`

## Interpretation
- The witness led the bounded symbolic control on both declared packet metrics in the mean.
- The packet is weak because both mean rank correlations are negative.
- The line therefore advances only through retained-model hardening, with no broader expansion.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/bridge_anchor_distance_v1.csv`
