# Q-RoPE Bridge Anchor-Betweenness Token-Renaming Hardening v1

## Hardening Packet
- perturbation: `token_permutation=cdab`
- retained models only:
  - `V_future_relational_witness_positional_anchor_betweenness`
  - `V_control_symbolic_positional_anchor_betweenness_regressor`

## Mean Hardening Results
- witness:
  - `mae = 0.080800`
  - `rank_correlation = 0.206349`
  - `calibration_slope = 0.341041`
- control:
  - `mae = 0.083308`
  - `rank_correlation = 0.103175`
  - `calibration_slope = 0.768238`
