# Q-RoPE E003 Position-Content First Packet v1

Date: 2026-03-14
Stories: S1366-S1369

## Fixed Packet
- dataset: `synthetic_positional_content_gated_offset_selection_response`
- witness: `V_future_relational_witness_positional_content_gated_offset_selection`
- control: `V_control_symbolic_positional_content_gated_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.034750`
  - `rank_correlation = 0.109471`
  - `calibration_slope = 0.601163`
- control:
  - `mae = 0.033607`
  - `rank_correlation = -0.038446`
  - `calibration_slope = -0.013623`

## Interpretation
- The first packet was mixed.
- The control kept mean `mae`.
- The witness kept mean `rank_correlation`.
- Under the declared two-metric gate, that is not a stop.

## Summary CSV
- `logs/ablation_runs/summary/E003_position_content_gated_offset_selection_v1.csv`
