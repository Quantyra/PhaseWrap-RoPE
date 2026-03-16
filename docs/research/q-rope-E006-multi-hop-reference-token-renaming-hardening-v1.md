# Q-RoPE E006 Multi-Hop Reference Token-Renaming Hardening v1

Date: 2026-03-16
Stories: S1458-S1460

## Fixed Hardening Packet
- dataset: `synthetic_positional_intermediate_pointer_selection_response`
- witness: `V_future_relational_witness_positional_intermediate_pointer_selection`
- control: `V_control_symbolic_positional_intermediate_pointer_selection_regressor`
- backend: `sim_quantum_statevector`
- token permutation: `cdab`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.001011`
  - `rank_correlation = -0.333333`
  - `calibration_slope = -0.096218`
- control:
  - `mae = 0.003471`
  - `rank_correlation = -0.333333`
  - `calibration_slope = -0.384685`

## Interpretation
- `token_permutation=cdab` was non-inert.
- The witness remained ahead on mean `mae`.
- Mean `rank_correlation` tied rather than flipping to the control.
- Under the declared two-metric gate, the branch remains active.

## Summary CSV
- `logs/ablation_runs/summary/E006_multi_hop_reference_cdab_v1.csv`
