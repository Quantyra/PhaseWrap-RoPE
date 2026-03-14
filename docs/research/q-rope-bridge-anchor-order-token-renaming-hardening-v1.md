# Q-RoPE Bridge Anchor-Order Token-Renaming Hardening v1

## Packet
- Perturbation: `token_permutation = cdab`
- Retained models:
  - `V_future_relational_witness_positional_anchor_order`
  - `V_control_symbolic_positional_anchor_order_regressor`

## Hardening Packet Means
- Witness:
  - `mae = 0.108051`
  - `rank_correlation = 0.268066`
  - `calibration_slope = 0.046033`
- Control:
  - `mae = 0.132873`
  - `rank_correlation = -0.372960`
  - `calibration_slope = -0.637492`

## Interpretation
- `token_permutation=cdab` was non-inert.
- The witness stayed ahead of the bounded symbolic control on both declared packet metrics in the mean.
- The bridge-task line advances to first structural hardening.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/bridge_anchor_order_cdab_v1.csv`
