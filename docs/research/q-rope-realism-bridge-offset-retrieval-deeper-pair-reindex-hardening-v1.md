# Q-RoPE Realism-Bridge Offset-Retrieval Deeper Pair-Reindex Hardening v1

## Hardening Packet
- perturbation: `pair_reindex=7`
- retained models only:
  - `V_future_relational_witness_positional_offset_retrieval`
  - `V_control_symbolic_positional_offset_retrieval_regressor`

## Mean Hardening Results
- witness:
  - `mae = 0.089465`
  - `rank_correlation = 0.317102`
  - `calibration_slope = 0.505266`
- control:
  - `mae = 0.101300`
  - `rank_correlation = -0.179130`
  - `calibration_slope = -0.318164`

## Summary CSV
- `logs/ablation_runs/summary/realism_bridge_offset_retrieval_pair7_v1.csv`
