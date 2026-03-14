# Q-RoPE Realism-Bridge Offset-Retrieval First Packet v1

## Fixed Packet
- dataset: `synthetic_positional_offset_retrieval_response`
- witness: `V_future_relational_witness_positional_offset_retrieval`
- control: `V_control_symbolic_positional_offset_retrieval_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.112647`
  - `rank_correlation = 0.084058`
  - `calibration_slope = -0.075769`
- control:
  - `mae = 0.116393`
  - `rank_correlation = -0.431304`
  - `calibration_slope = -0.574163`

## Summary CSV
- `logs/ablation_runs/summary/realism_bridge_offset_retrieval_v1.csv`
