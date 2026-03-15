# Q-RoPE E002 Variable-Cardinality Slot-Swap Hardening v1

Date: 2026-03-14
Stories: S1344-S1346

## BLUF
- `slot_swap=1` was non-inert.
- The witness remained ahead of the bounded symbolic control on both declared mean gate metrics.
- `E002` stays active and advances only to the closure packet `pair_reindex=7`.

## Fixed Hardening Packet
- dataset: `synthetic_positional_variable_cardinality_offset_selection_response`
- witness: `V_future_relational_witness_positional_variable_cardinality_offset_selection`
- control: `V_control_symbolic_positional_variable_cardinality_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- slot swap: `1`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.047901`
  - `rank_correlation = 0.480852`
  - `calibration_slope = 0.883896`
- control:
  - `mae = 0.058272`
  - `rank_correlation = 0.135011`
  - `calibration_slope = 0.152640`

## Summary CSV
- `logs/ablation_runs/summary/E002_variable_cardinality_offset_selection_slot1_v1.csv`
