# Q-RoPE E007 Reference Revision Token-Renaming Hardening v1

Date: 2026-03-16
Stories: S1490-S1492

## Fixed Packet
- dataset: `synthetic_positional_reference_revision_selection_response`
- perturbation: `token_permutation=cdab`
- witness: `V_future_relational_witness_positional_reference_revision_selection`
- control: `V_control_symbolic_positional_reference_revision_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.022946`
  - `rank_correlation = 0.295800`
  - `calibration_slope = 0.839393`
- control:
  - `mae = 11.917032`
  - `rank_correlation = -0.093063`
  - `calibration_slope = 0.042266`

## Interpretation
- `token_permutation=cdab` was strongly non-inert.
- The witness remained ahead on both declared mean packet metrics.
- The bounded symbolic control suffered a large one-seed `mae` blow-up under renaming and did not recover the two-metric gate overall.
- Under protocol, the line remains active and advances only to the first structural hardening step.

## Summary CSV
- `logs/ablation_runs/summary/E007_reference_revision_cdab_v1.csv`
