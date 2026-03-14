# Q-RoPE Bridge Anchor-Distance Pair-Reindex Hardening v1

## Hardening Packet Means
- Witness:
  - `mae = 0.124019`
  - `rank_correlation = -0.666667`
  - `calibration_slope = -0.512541`
- Control:
  - `mae = 0.127504`
  - `rank_correlation = 0.066667`
  - `calibration_slope = 0.533565`

## Interpretation
- `pair_reindex=1` was non-inert.
- The line became mixed on the declared packet metrics: witness kept mean `mae`, control took mean `rank_correlation`.
- Under the declared stop rule, mixed leadership is not enough to stop the line.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/bridge_anchor_distance_pair1_v1.csv`
