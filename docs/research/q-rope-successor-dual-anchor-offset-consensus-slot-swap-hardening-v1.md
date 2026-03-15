# Q-RoPE Successor Dual-Anchor Offset-Consensus Slot-Swap Hardening v1

## Fixed Hardening Packet
- dataset: `synthetic_positional_dual_anchor_offset_consensus_response`
- witness: `V_future_relational_witness_positional_dual_anchor_offset_consensus`
- control: `V_control_symbolic_positional_dual_anchor_offset_consensus_regressor`
- backend: `sim_quantum_statevector`
- slot swap: `1`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.029820`
  - `rank_correlation = 0.303760`
  - `calibration_slope = 0.558087`
- control:
  - `mae = 0.031362`
  - `rank_correlation = 0.188369`
  - `calibration_slope = 0.301798`

## Summary CSV
- `logs/ablation_runs/summary/successor_dual_anchor_offset_consensus_slot1_v1.csv`
