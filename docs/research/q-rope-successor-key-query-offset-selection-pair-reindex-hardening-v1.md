# Q-RoPE Successor Key-Query Offset Selection Pair-Reindex Hardening v1

## Fixed Hardening Packet
- dataset: `synthetic_positional_key_query_offset_selection_response`
- perturbation: `pair_reindex=1`
- witness: `V_future_relational_witness_positional_key_query_offset_selection`
- control: `V_control_symbolic_positional_key_query_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.058901`
  - `rank_correlation = 0.582215`
  - `calibration_slope = 0.801202`
- control:
  - `mae = 0.082388`
  - `rank_correlation = -0.045844`
  - `calibration_slope = -0.161243`

## Summary CSV
- `logs/ablation_runs/summary/successor_key_query_offset_selection_pair1_v1.csv`
