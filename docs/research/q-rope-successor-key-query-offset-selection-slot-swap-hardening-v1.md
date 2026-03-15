# Q-RoPE Successor Key-Query Offset Selection Slot-Swap Hardening v1

## Fixed Hardening Packet
- dataset: `synthetic_positional_key_query_offset_selection_response`
- perturbation: `slot_swap=1`
- witness: `V_future_relational_witness_positional_key_query_offset_selection`
- control: `V_control_symbolic_positional_key_query_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.067198`
  - `rank_correlation = 0.503286`
  - `calibration_slope = 1.066303`
- control:
  - `mae = 0.082179`
  - `rank_correlation = 0.310856`
  - `calibration_slope = 0.955326`

## Summary CSV
- `logs/ablation_runs/summary/successor_key_query_offset_selection_slot1_v1.csv`
