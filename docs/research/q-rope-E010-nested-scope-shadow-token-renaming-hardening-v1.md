# Q-RoPE E010 Nested-Scope Shadow Token-Renaming Hardening v1

Date: 2026-03-17
Stories: S1586-S1588

## Fixed Packet
- dataset: `synthetic_positional_nested_scope_shadow_selection_response`
- perturbation: `token_permutation=cdab`
- witness: `V_future_relational_witness_positional_nested_scope_shadow_selection`
- control: `V_control_symbolic_positional_nested_scope_shadow_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.011326`
  - `rank_correlation = 0.442668`
  - `calibration_slope = 1.018145`
- control:
  - `mae = 0.014331`
  - `rank_correlation = 0.110104`
  - `calibration_slope = 0.581388`

## Interpretation
- `token_permutation=cdab` was non-inert.
- The witness remained ahead on both declared mean packet metrics.
- The next valid move is the fixed structural hardening packet `pair_reindex=1` only.

## Summary CSV
- `logs/ablation_runs/summary/E010_nested_scope_shadow_cdab_v1.csv`
