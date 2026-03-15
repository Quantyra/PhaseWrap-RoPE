# Q-RoPE Successor Dual-Anchor Offset-Consensus Token-Renaming Hardening v1

## Fixed Hardening Packet
- dataset: `synthetic_positional_dual_anchor_offset_consensus_response`
- witness: `V_future_relational_witness_positional_dual_anchor_offset_consensus`
- control: `V_control_symbolic_positional_dual_anchor_offset_consensus_regressor`
- backend: `sim_quantum_statevector`
- token permutation: `cdab`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.039379`
  - `rank_correlation = 0.137866`
  - `calibration_slope = 0.286595`
- control:
  - `mae = 0.039139`
  - `rank_correlation = 0.040588`
  - `calibration_slope = 0.387073`

## Summary CSV
- `logs/ablation_runs/summary/successor_dual_anchor_offset_consensus_cdab_v1.csv`
