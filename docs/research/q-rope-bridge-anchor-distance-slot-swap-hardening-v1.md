# Q-RoPE Bridge Anchor-Distance Slot-Swap Hardening v1

## Hardening Packet Means
- Witness:
  - `mae = 0.212503`
  - `rank_correlation = -0.333333`
  - `calibration_slope = -0.156201`
- Control:
  - `mae = 0.218497`
  - `rank_correlation = -0.266667`
  - `calibration_slope = -0.838046`

## Interpretation
- `slot_swap=1` was non-inert.
- The line stayed mixed on the declared packet metrics: witness kept mean `mae`, control kept the less-negative mean `rank_correlation`.
- The control still did not clear the two-metric stop rule.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/bridge_anchor_distance_slot1_v1.csv`
