# Q-RoPE E005 Shared-Memory Multi-Query First Packet v1

Date: 2026-03-15
Stories: S1431-S1434

## Fixed Packet
- dataset: `synthetic_positional_shared_memory_multi_query_selection_response`
- witness: `V_future_relational_witness_positional_shared_memory_multi_query_selection`
- control: `V_control_symbolic_positional_shared_memory_multi_query_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.030070`
  - `rank_correlation = -0.131720`
  - `calibration_slope = -0.014515`
- control:
  - `mae = 0.031196`
  - `rank_correlation = -0.338024`
  - `calibration_slope = -0.520674`

## Interpretation
- The witness led on both declared mean gate metrics.
- The shared-memory task stayed bounded and auditable across candidate counts `3`, `4`, and `5`.
- Under the declared two-metric gate, the branch remains active.

## Summary CSV
- `logs/ablation_runs/summary/E005_shared_memory_multi_query_selection_v1.csv`
