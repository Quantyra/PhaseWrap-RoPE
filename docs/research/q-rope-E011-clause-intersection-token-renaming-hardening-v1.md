# Q-RoPE E011 Clause-Intersection Token-Renaming Hardening v1

Date: 2026-03-19
Stories: S1618-S1620

## Fixed Packet
- dataset: `synthetic_positional_clause_intersection_reference_selection_response`
- perturbation: `token_permutation=cdab`
- witness: `V_future_relational_witness_positional_clause_intersection_reference_selection`
- control: `V_control_symbolic_positional_clause_intersection_reference_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.033113`
  - `rank_correlation = 0.241307`
  - `calibration_slope = 0.685056`
- control:
  - `mae = 0.033465`
  - `rank_correlation = 0.152012`
  - `calibration_slope = 0.288062`

## Interpretation
- `token_permutation=cdab` was non-inert.
- The witness remained ahead on both declared mean packet metrics.
- The next valid move is the fixed structural hardening packet `pair_reindex=1` only.

## Summary CSV
- `logs/ablation_runs/summary/E011_clause_intersection_cdab_v1.csv`
