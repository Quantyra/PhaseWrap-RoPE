# Q-RoPE E007 Reference Revision First Packet v1

Date: 2026-03-16
Stories: S1486-S1489

## Fixed Packet
- dataset: `synthetic_positional_reference_revision_selection_response`
- witness: `V_future_relational_witness_positional_reference_revision_selection`
- control: `V_control_symbolic_positional_reference_revision_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.027358`
  - `rank_correlation = 0.434812`
  - `calibration_slope = 0.685859`
- control:
  - `mae = 0.033747`
  - `rank_correlation = 0.068732`
  - `calibration_slope = -0.205764`

## Interpretation
- The witness beat the bounded symbolic control on both declared mean packet metrics.
- The revision-validity task stayed within the frozen stale/current fairness contract.
- The line has earned exactly one next move: retained nuisance hardening with `token_permutation=cdab`.

## Summary CSV
- `logs/ablation_runs/summary/E007_reference_revision_v1.csv`
