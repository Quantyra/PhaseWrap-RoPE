# Q-RoPE Realism-Bridge Offset-Retrieval Token-Renaming Hardening v1

## Hardening Packet
- perturbation: `token_permutation=cdab`
- retained models only:
  - `V_future_relational_witness_positional_offset_retrieval`
  - `V_control_symbolic_positional_offset_retrieval_regressor`

## Mean Hardening Results
- witness:
  - `mae = 0.075417`
  - `rank_correlation = 0.452737`
  - `calibration_slope = 0.363013`
- control:
  - `mae = 0.085334`
  - `rank_correlation = -0.049909`
  - `calibration_slope = -0.188416`

## Summary CSV
- `logs/ablation_runs/summary/realism_bridge_offset_retrieval_cdab_v1.csv`
