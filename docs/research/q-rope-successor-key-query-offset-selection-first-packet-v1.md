# Q-RoPE Successor Key-Query Offset Selection First Packet v1

## Fixed Packet
- dataset: `synthetic_positional_key_query_offset_selection_response`
- witness: `V_future_relational_witness_positional_key_query_offset_selection`
- control: `V_control_symbolic_positional_key_query_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.050993`
  - `rank_correlation = 0.571859`
  - `calibration_slope = 0.675304`
- control:
  - `mae = 0.077298`
  - `rank_correlation = -0.012068`
  - `calibration_slope = -0.209734`

## Summary CSV
- `logs/ablation_runs/summary/successor_key_query_offset_selection_v1.csv`
