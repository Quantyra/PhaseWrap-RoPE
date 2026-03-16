# Q-RoPE E006 Multi-Hop Reference Deeper Pair-Reindex Hardening v1

Date: 2026-03-16
Stories: S1467-S1470

## Fixed Hardening Packet
- dataset: `synthetic_positional_intermediate_pointer_selection_response`
- witness: `V_future_relational_witness_positional_intermediate_pointer_selection`
- control: `V_control_symbolic_positional_intermediate_pointer_selection_regressor`
- backend: `sim_quantum_statevector`
- pair reindex: `7`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.004690`
  - `rank_correlation = 0.000000`
  - `calibration_slope = 0.000000`
- control:
  - `mae = 0.010673`
  - `rank_correlation = 0.000000`
  - `calibration_slope = 0.000000`

## Interpretation
- `pair_reindex=7` was non-inert.
- The witness remained ahead on mean `mae`.
- Mean `rank_correlation` tied rather than flipping to the control.
- The closure packet preserved the line under the declared two-metric gate.

## Summary CSV
- `logs/ablation_runs/summary/E006_multi_hop_reference_pair7_v1.csv`
