# Q-RoPE E003 Position-Content Token-Renaming Hardening v1

Date: 2026-03-14
Stories: S1370-S1372

## Fixed Hardening Packet
- dataset: `synthetic_positional_content_gated_offset_selection_response`
- witness: `V_future_relational_witness_positional_content_gated_offset_selection`
- control: `V_control_symbolic_positional_content_gated_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- token permutation: `cdab`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.034951`
  - `rank_correlation = 0.430658`
  - `calibration_slope = 0.882071`
- control:
  - `mae = 0.041872`
  - `rank_correlation = -0.012222`
  - `calibration_slope = -0.237720`

## Interpretation
- `token_permutation=cdab` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The line strengthened relative to the mixed first packet.

## Summary CSV
- `logs/ablation_runs/summary/E003_position_content_gated_offset_selection_cdab_v1.csv`
