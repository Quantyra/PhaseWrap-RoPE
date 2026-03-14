# Q-RoPE Bridge Anchor-Betweenness Slot-Swap Hardening v1

## Hardening Packet
- perturbation: `slot_swap=1`
- retained models only:
  - `V_future_relational_witness_positional_anchor_betweenness`
  - `V_control_symbolic_positional_anchor_betweenness_regressor`

## Mean Hardening Results
- witness:
  - `mae = 0.086015`
  - `rank_correlation = -0.460317`
  - `calibration_slope = -0.857828`
- control:
  - `mae = 0.081210`
  - `rank_correlation = -0.222222`
  - `calibration_slope = -0.594902`
