# Q-RoPE Realism-Bridge Offset-Retrieval Slot-Swap Hardening v1

## Hardening Packet
- perturbation: `slot_swap=1`
- retained models only:
  - `V_future_relational_witness_positional_offset_retrieval`
  - `V_control_symbolic_positional_offset_retrieval_regressor`

## Mean Hardening Results
- witness:
  - `mae = 0.096670`
  - `rank_correlation = -0.124638`
  - `calibration_slope = -0.203034`
- control:
  - `mae = 0.093190`
  - `rank_correlation = -0.136232`
  - `calibration_slope = -0.282699`

## Summary CSV
- `logs/ablation_runs/summary/realism_bridge_offset_retrieval_slot1_v1.csv`
