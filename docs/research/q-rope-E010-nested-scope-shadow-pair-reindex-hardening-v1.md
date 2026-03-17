# Q-RoPE E010 Nested-Scope Shadow Pair-Reindex Hardening v1

Date: 2026-03-17
Stories: S1589-S1591

## Fixed Packet
- dataset: `synthetic_positional_nested_scope_shadow_selection_response`
- perturbation: `pair_reindex=1`
- witness: `V_future_relational_witness_positional_nested_scope_shadow_selection`
- control: `V_control_symbolic_positional_nested_scope_shadow_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.011874`
  - `rank_correlation = 0.182638`
  - `calibration_slope = 0.438914`
- control:
  - `mae = 0.014758`
  - `rank_correlation = -0.144497`
  - `calibration_slope = -0.639585`

## Interpretation
- `pair_reindex=1` was non-inert.
- The witness remained ahead on both declared mean packet metrics.
- The next valid move is the fixed structural hardening packet `slot_swap=1` only.

## Summary CSV
- `logs/ablation_runs/summary/E010_nested_scope_shadow_pair1_v1.csv`
