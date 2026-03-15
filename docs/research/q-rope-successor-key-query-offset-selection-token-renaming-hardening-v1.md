# Q-RoPE Successor Key-Query Offset Selection Token-Renaming Hardening v1

## Fixed Hardening Packet
- dataset: `synthetic_positional_key_query_offset_selection_response`
- perturbation: `token_permutation=cdab`
- witness: `V_future_relational_witness_positional_key_query_offset_selection`
- control: `V_control_symbolic_positional_key_query_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.043415`
  - `rank_correlation = 0.503784`
  - `calibration_slope = 0.857687`
- control:
  - `mae = 0.052165`
  - `rank_correlation = 0.302508`
  - `calibration_slope = 1.161087`

## Summary CSV
- `logs/ablation_runs/summary/successor_key_query_offset_selection_cdab_v1.csv`
