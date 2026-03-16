# Q-RoPE E006 Multi-Hop Reference First Packet v1

Date: 2026-03-16
Stories: S1454-S1460

## Fixed Packet
- dataset: `synthetic_positional_intermediate_pointer_selection_response`
- witness: `V_future_relational_witness_positional_intermediate_pointer_selection`
- control: `V_control_symbolic_positional_intermediate_pointer_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.000770`
  - `rank_correlation = 0.000000`
  - `calibration_slope = 0.000000`
- control:
  - `mae = 0.001782`
  - `rank_correlation = 0.000000`
  - `calibration_slope = 0.000000`

## Interpretation
- The witness led on mean `mae`.
- Mean `rank_correlation` tied at `0.000000` for both paths.
- Under the declared two-metric gate, the branch remains active because the control did not match or beat the witness on both declared mean metrics.

## Summary CSV
- `logs/ablation_runs/summary/E006_multi_hop_reference_v1.csv`
