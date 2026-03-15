# Q-RoPE Successor Dual-Anchor Offset-Consensus Pair-Reindex Hardening v1

## Fixed Hardening Packet
- dataset: `synthetic_positional_dual_anchor_offset_consensus_response`
- witness: `V_future_relational_witness_positional_dual_anchor_offset_consensus`
- control: `V_control_symbolic_positional_dual_anchor_offset_consensus_regressor`
- backend: `sim_quantum_statevector`
- pair reindex: `1`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.025092`
  - `rank_correlation = 0.282433`
  - `calibration_slope = 0.693252`
- control:
  - `mae = 0.027074`
  - `rank_correlation = 0.024256`
  - `calibration_slope = 0.109949`

## Summary CSV
- `logs/ablation_runs/summary/successor_dual_anchor_offset_consensus_pair1_v1.csv`
