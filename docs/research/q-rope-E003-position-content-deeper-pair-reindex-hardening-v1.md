# Q-RoPE E003 Position-Content Deeper Pair-Reindex Hardening v1

Date: 2026-03-15
Stories: S1379-S1382

## Fixed Hardening Packet
- dataset: `synthetic_positional_content_gated_offset_selection_response`
- witness: `V_future_relational_witness_positional_content_gated_offset_selection`
- control: `V_control_symbolic_positional_content_gated_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- pair reindex: `7`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.044039`
  - `rank_correlation = 0.080192`
  - `calibration_slope = 0.587101`
- control:
  - `mae = 0.044573`
  - `rank_correlation = -0.059415`
  - `calibration_slope = -0.145803`

## Interpretation
- `pair_reindex=7` was non-inert.
- The witness remained ahead on both declared mean gate metrics, but the mean rank margin narrowed materially relative to the earlier structural packets.
- The line survived the full retained hardening ladder and returns to memo-only preserved state.

## Summary CSV
- `logs/ablation_runs/summary/E003_position_content_gated_offset_selection_pair7_v1.csv`
