# Q-RoPE E002 Variable-Cardinality Token-Renaming Hardening v1

Date: 2026-03-14
Stories: S1338-S1340

## Fixed Hardening Packet
- dataset: `synthetic_positional_variable_cardinality_offset_selection_response`
- witness: `V_future_relational_witness_positional_variable_cardinality_offset_selection`
- control: `V_control_symbolic_positional_variable_cardinality_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- token permutation: `cdab`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.044289`
  - `rank_correlation = 0.626567`
  - `calibration_slope = 0.831236`
- control:
  - `mae = 0.054139`
  - `rank_correlation = 0.298294`
  - `calibration_slope = 1.107336`

## Summary CSV
- `logs/ablation_runs/summary/E002_variable_cardinality_offset_selection_cdab_v1.csv`
