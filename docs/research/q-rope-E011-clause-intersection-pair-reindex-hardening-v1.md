# Q-RoPE E011 Clause-Intersection Pair-Reindex Hardening v1

Date: 2026-03-19
Stories: S1621-S1623

## Fixed Packet
- dataset: `synthetic_positional_clause_intersection_reference_selection_response`
- perturbation: `pair_reindex=1`
- witness: `V_future_relational_witness_positional_clause_intersection_reference_selection`
- control: `V_control_symbolic_positional_clause_intersection_reference_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.031553`
  - `rank_correlation = 0.386196`
  - `calibration_slope = 0.873276`
- control:
  - `mae = 0.035457`
  - `rank_correlation = 0.053067`
  - `calibration_slope = -0.066943`

## Interpretation
- `pair_reindex=1` was non-inert.
- The witness remained ahead on both declared mean packet metrics.
- The next valid move is the fixed structural hardening packet `slot_swap=1` only.

## Summary CSV
- `logs/ablation_runs/summary/E011_clause_intersection_pair1_v1.csv`
