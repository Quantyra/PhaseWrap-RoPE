# Q-RoPE E002 Variable-Cardinality Deeper Pair-Reindex Hardening v1

Date: 2026-03-14
Stories: S1347-S1350

## BLUF
- The closure packet `pair_reindex=7` was non-inert.
- The witness remained ahead of the bounded symbolic control on both declared mean gate metrics.
- `E002` survived the full bounded hardening cycle and returns to memo-only preserved state.

## Fixed Hardening Packet
- dataset: `synthetic_positional_variable_cardinality_offset_selection_response`
- witness: `V_future_relational_witness_positional_variable_cardinality_offset_selection`
- control: `V_control_symbolic_positional_variable_cardinality_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- pair reindex: `7`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.048029`
  - `rank_correlation = 0.320957`
  - `calibration_slope = 1.026276`
- control:
  - `mae = 0.050783`
  - `rank_correlation = 0.064808`
  - `calibration_slope = 0.439376`

## Summary CSV
- `logs/ablation_runs/summary/E002_variable_cardinality_offset_selection_pair7_v1.csv`
