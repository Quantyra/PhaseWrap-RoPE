# Q-RoPE Bridge Anchor-Distance Token-Renaming Hardening v1

## Hardening Packet Means
- Witness:
  - `mae = 0.138297`
  - `rank_correlation = 0.200000`
  - `calibration_slope = 0.517916`
- Control:
  - `mae = 0.215227`
  - `rank_correlation = -0.600000`
  - `calibration_slope = -0.643027`

## Interpretation
- `token_permutation=cdab` was non-inert.
- The witness stayed ahead on both declared packet metrics in the mean.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/bridge_anchor_distance_cdab_v1.csv`
