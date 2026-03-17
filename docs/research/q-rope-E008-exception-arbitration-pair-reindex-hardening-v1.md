# Q-RoPE E008 Exception Arbitration Pair-Reindex Hardening v1

Date: 2026-03-16
Stories: S1525-S1527

## Fixed Packet
- dataset: `synthetic_positional_exception_conditioned_reference_selection_response`
- perturbation: `pair_reindex=1`
- witness: `V_future_relational_witness_positional_exception_conditioned_reference_selection`
- control: `V_control_symbolic_positional_exception_conditioned_reference_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.024152`
  - `rank_correlation = 0.182358`
  - `calibration_slope = 0.291077`
- control:
  - `mae = 0.025733`
  - `rank_correlation = -0.078591`
  - `calibration_slope = 0.213232`

## Interpretation
- `pair_reindex=1` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The first structural packet preserved the line rather than collapsing it.

## Summary CSV
- `logs/ablation_runs/summary/E008_exception_arbitration_pair1_v1.csv`
