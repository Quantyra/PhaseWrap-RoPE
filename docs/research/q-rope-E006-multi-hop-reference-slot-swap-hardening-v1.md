# Q-RoPE E006 Multi-Hop Reference Slot-Swap Hardening v1

Date: 2026-03-16
Stories: S1464-S1466

## Fixed Hardening Packet
- dataset: `synthetic_positional_intermediate_pointer_selection_response`
- witness: `V_future_relational_witness_positional_intermediate_pointer_selection`
- control: `V_control_symbolic_positional_intermediate_pointer_selection_regressor`
- backend: `sim_quantum_statevector`
- slot swap: `1`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.011765`
  - `rank_correlation = 0.666667`
  - `calibration_slope = 0.673273`
- control:
  - `mae = 0.033226`
  - `rank_correlation = 0.000000`
  - `calibration_slope = -1.964624`

## Interpretation
- `slot_swap=1` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The second structural packet preserved and strengthened the line.

## Summary CSV
- `logs/ablation_runs/summary/E006_multi_hop_reference_slot1_v1.csv`
