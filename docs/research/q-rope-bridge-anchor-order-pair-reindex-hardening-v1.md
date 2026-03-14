# Q-RoPE Bridge Anchor-Order Pair-Reindex Hardening v1

## Packet
- Perturbation: `pair_reindex = 1`
- Retained models:
  - `V_future_relational_witness_positional_anchor_order`
  - `V_control_symbolic_positional_anchor_order_regressor`

## Hardening Packet Means
- Witness:
  - `mae = 0.156054`
  - `rank_correlation = 0.163170`
  - `calibration_slope = 0.162744`
- Control:
  - `mae = 0.162997`
  - `rank_correlation = -0.111888`
  - `calibration_slope = -0.124406`

## Interpretation
- `pair_reindex=1` was non-inert.
- The witness stayed ahead of the bounded symbolic control on both declared packet metrics in the mean.
- The bridge-task line advances to the fixed `slot_swap=1` structural packet.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/bridge_anchor_order_pair1_v1.csv`
