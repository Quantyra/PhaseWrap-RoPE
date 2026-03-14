# Q-RoPE Bridge Anchor-Betweenness Pair-Reindex Hardening v1

## Hardening Packet
- perturbation: `pair_reindex=1`
- retained models only:
  - `V_future_relational_witness_positional_anchor_betweenness`
  - `V_control_symbolic_positional_anchor_betweenness_regressor`

## Mean Hardening Results
- witness:
  - `mae = 0.111634`
  - `rank_correlation = -0.373016`
  - `calibration_slope = -0.086975`
- control:
  - `mae = 0.117203`
  - `rank_correlation = -0.388889`
  - `calibration_slope = -0.297850`
