# Q-RoPE E003 Position-Content Slot-Swap Hardening v1

Date: 2026-03-15
Stories: S1376-S1378

## Fixed Hardening Packet
- dataset: `synthetic_positional_content_gated_offset_selection_response`
- witness: `V_future_relational_witness_positional_content_gated_offset_selection`
- control: `V_control_symbolic_positional_content_gated_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- slot swap: `1`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.044584`
  - `rank_correlation = 0.456014`
  - `calibration_slope = 0.914409`
- control:
  - `mae = 0.052493`
  - `rank_correlation = -0.164838`
  - `calibration_slope = -0.719229`

## Interpretation
- `slot_swap=1` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The second structural packet preserved the line rather than narrowing it.

## Summary CSV
- `logs/ablation_runs/summary/E003_position_content_gated_offset_selection_slot1_v1.csv`
