# Q-RoPE E011 Clause-Intersection Slot-Swap Hardening v1

Date: 2026-03-19
Stories: S1624-S1626

## Fixed Packet
- dataset: `synthetic_positional_clause_intersection_reference_selection_response`
- perturbation: `slot_swap=1`
- witness: `V_future_relational_witness_positional_clause_intersection_reference_selection`
- control: `V_control_symbolic_positional_clause_intersection_reference_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.028963`
  - `rank_correlation = 0.334033`
  - `calibration_slope = 0.635544`
- control:
  - `mae = 0.030492`
  - `rank_correlation = 0.075172`
  - `calibration_slope = 0.088885`

## Interpretation
- `slot_swap=1` was non-inert.
- The witness remained ahead on both declared mean packet metrics.
- The next valid move is the closure packet `pair_reindex=7` only.

## Summary CSV
- `logs/ablation_runs/summary/E011_clause_intersection_slot1_v1.csv`
