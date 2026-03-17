# Q-RoPE E009 Scope-Masking Token-Renaming Hardening v1

Date: 2026-03-16
Stories: S1554-S1556

## Fixed Packet
- dataset: `synthetic_positional_scope_masked_reference_selection_response`
- perturbation: `token_permutation=cdab`
- witness: `V_future_relational_witness_positional_scope_masked_reference_selection`
- control: `V_control_symbolic_positional_scope_masked_reference_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.024017`
  - `rank_correlation = 0.305837`
  - `calibration_slope = 0.888792`
- control:
  - `mae = 0.026644`
  - `rank_correlation = -0.005022`
  - `calibration_slope = -0.124231`

## Interpretation
- `token_permutation=cdab` was non-inert.
- The witness remained ahead on both declared mean packet metrics.
- The next valid move is the fixed structural hardening packet `pair_reindex=1` only.

## Summary CSV
- `logs/ablation_runs/summary/E009_scope_masking_cdab_v1.csv`
