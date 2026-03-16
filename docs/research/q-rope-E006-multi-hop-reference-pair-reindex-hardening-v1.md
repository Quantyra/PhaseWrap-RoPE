# Q-RoPE E006 Multi-Hop Reference Pair-Reindex Hardening v1

Date: 2026-03-16
Stories: S1461-S1463

## Fixed Hardening Packet
- dataset: `synthetic_positional_intermediate_pointer_selection_response`
- witness: `V_future_relational_witness_positional_intermediate_pointer_selection`
- control: `V_control_symbolic_positional_intermediate_pointer_selection_regressor`
- backend: `sim_quantum_statevector`
- pair reindex: `1`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.008702`
  - `rank_correlation = 0.000000`
  - `calibration_slope = -9.889104`
- control:
  - `mae = 0.013885`
  - `rank_correlation = -0.666667`
  - `calibration_slope = -2.509523`

## Interpretation
- `pair_reindex=1` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The first structural packet strengthened the line relative to the retained nuisance packet.

## Summary CSV
- `logs/ablation_runs/summary/E006_multi_hop_reference_pair1_v1.csv`
