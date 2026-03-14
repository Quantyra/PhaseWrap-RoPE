# Q-RoPE Bridge Anchor-Distance Deeper Pair-Reindex Hardening v1

## Hardening Packet Means
- Witness:
  - `mae = 0.122907`
  - `rank_correlation = -0.466667`
  - `calibration_slope = -0.124108`
- Control:
  - `mae = 0.144214`
  - `rank_correlation = -0.466667`
  - `calibration_slope = -0.377375`

## Interpretation
- `pair_reindex=7` was non-inert.
- Mean `rank_correlation` tied while the witness kept lower mean `mae`.
- The control never matched or beat the witness on both declared packet metrics.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/bridge_anchor_distance_pair7_v1.csv`
