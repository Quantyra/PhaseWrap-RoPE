# Q-RoPE E002 Variable-Cardinality Pair-Reindex Hardening v1

Date: 2026-03-14
Stories: S1341-S1343

## BLUF
- `pair_reindex=1` was non-inert.
- The witness remained ahead of the bounded symbolic control on both declared mean gate metrics.
- `E002` stays active and advances only to the fixed `slot_swap=1` structural hardening packet.

## Fixed Hardening Packet
- dataset: `synthetic_positional_variable_cardinality_offset_selection_response`
- witness: `V_future_relational_witness_positional_variable_cardinality_offset_selection`
- control: `V_control_symbolic_positional_variable_cardinality_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- pair reindex: `1`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.049239`
  - `rank_correlation = 0.495142`
  - `calibration_slope = 1.001644`
- control:
  - `mae = 0.056428`
  - `rank_correlation = 0.224468`
  - `calibration_slope = 0.816948`

## Summary CSV
- `logs/ablation_runs/summary/E002_variable_cardinality_offset_selection_pair1_v1.csv`
