# Q-RoPE Successor Dual-Anchor Offset-Consensus Deeper Pair-Reindex Hardening v1

## Fixed Hardening Packet
- dataset: `synthetic_positional_dual_anchor_offset_consensus_response`
- witness: `V_future_relational_witness_positional_dual_anchor_offset_consensus`
- control: `V_control_symbolic_positional_dual_anchor_offset_consensus_regressor`
- backend: `sim_quantum_statevector`
- pair reindex: `7`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.026446`
  - `rank_correlation = 0.391270`
  - `calibration_slope = 0.700340`
- control:
  - `mae = 0.028572`
  - `rank_correlation = 0.261100`
  - `calibration_slope = 0.761915`

## Summary CSV
- `logs/ablation_runs/summary/successor_dual_anchor_offset_consensus_pair7_v1.csv`
