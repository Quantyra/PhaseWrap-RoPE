# Q-RoPE E008 Exception Arbitration Deeper Pair-Reindex Hardening v1

Date: 2026-03-16
Stories: S1531-S1534

## Fixed Packet
- dataset: `synthetic_positional_exception_conditioned_reference_selection_response`
- perturbation: `pair_reindex=7`
- witness: `V_future_relational_witness_positional_exception_conditioned_reference_selection`
- control: `V_control_symbolic_positional_exception_conditioned_reference_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.017637`
  - `rank_correlation = 0.422078`
  - `calibration_slope = 0.648987`
- control:
  - `mae = 0.020193`
  - `rank_correlation = 0.141956`
  - `calibration_slope = 0.432263`

## Interpretation
- `pair_reindex=7` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The line survived the full bounded hardening ladder and qualifies for preservation rather than further default perturbation expansion.

## Summary CSV
- `logs/ablation_runs/summary/E008_exception_arbitration_pair7_v1.csv`
