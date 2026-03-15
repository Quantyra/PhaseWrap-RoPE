# Q-RoPE Successor Dual-Anchor Offset-Consensus First Packet v1

## Fixed Packet
- dataset: `synthetic_positional_dual_anchor_offset_consensus_response`
- witness: `V_future_relational_witness_positional_dual_anchor_offset_consensus`
- control: `V_control_symbolic_positional_dual_anchor_offset_consensus_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.037918`
  - `rank_correlation = 0.425748`
  - `calibration_slope = 0.839088`
- control:
  - `mae = 0.042120`
  - `rank_correlation = -0.040158`
  - `calibration_slope = -0.235951`

## Summary CSV
- `logs/ablation_runs/summary/successor_dual_anchor_offset_consensus_v1.csv`
