# Q-RoPE Bridge Anchor-Order Slot-Swap Hardening v1

## Packet
- Perturbation: `slot_swap = 1`
- Retained models:
  - `V_future_relational_witness_positional_anchor_order`
  - `V_control_symbolic_positional_anchor_order_regressor`

## Hardening Packet Means
- Witness:
  - `mae = 0.139765`
  - `rank_correlation = 0.170163`
  - `calibration_slope = 0.181778`
- Control:
  - `mae = 0.153458`
  - `rank_correlation = -0.349650`
  - `calibration_slope = -0.386913`

## Interpretation
- `slot_swap=1` was non-inert.
- The witness stayed ahead on both declared packet metrics in the mean.
- The bridge-task line advances to the deeper structural packet.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/bridge_anchor_order_slot1_v1.csv`
