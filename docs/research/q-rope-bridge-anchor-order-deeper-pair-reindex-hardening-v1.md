# Q-RoPE Bridge Anchor-Order Deeper Pair-Reindex Hardening v1

## Packet
- Perturbation: `pair_reindex = 7`
- Retained models:
  - `V_future_relational_witness_positional_anchor_order`
  - `V_control_symbolic_positional_anchor_order_regressor`

## Hardening Packet Means
- Witness:
  - `mae = 0.119600`
  - `rank_correlation = 0.195804`
  - `calibration_slope = 0.121728`
- Control:
  - `mae = 0.141610`
  - `rank_correlation = -0.282051`
  - `calibration_slope = -0.330414`

## Interpretation
- `pair_reindex=7` was non-inert.
- The witness stayed ahead on both declared packet metrics in the mean.
- This closes the retained-model hardening cycle for the first bridge-task line.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/bridge_anchor_order_pair7_v1.csv`
