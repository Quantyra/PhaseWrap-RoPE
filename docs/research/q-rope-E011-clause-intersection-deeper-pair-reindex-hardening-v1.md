# Q-RoPE E011 Clause-Intersection Deeper Pair-Reindex Hardening v1

Date: 2026-03-19
Stories: S1627-S1630

## Fixed Packet
- dataset: `synthetic_positional_clause_intersection_reference_selection_response`
- perturbation: `pair_reindex=7`
- witness: `V_future_relational_witness_positional_clause_intersection_reference_selection`
- control: `V_control_symbolic_positional_clause_intersection_reference_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.033772`
  - `rank_correlation = 0.364561`
  - `calibration_slope = 0.641689`
- control:
  - `mae = 0.039910`
  - `rank_correlation = -0.135232`
  - `calibration_slope = -0.291576`

## Interpretation
- `pair_reindex=7` was non-inert.
- The witness remained ahead on both declared mean packet metrics.
- The accepted E011 line survived the retained nuisance packet and all retained structural packets.

## Summary CSV
- `logs/ablation_runs/summary/E011_clause_intersection_pair7_v1.csv`
