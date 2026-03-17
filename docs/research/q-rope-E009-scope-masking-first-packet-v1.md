# Q-RoPE E009 Scope-Masking First Packet v1

Date: 2026-03-16
Stories: S1550-S1553

## Fixed Packet
- dataset: `synthetic_positional_scope_masked_reference_selection_response`
- witness: `V_future_relational_witness_positional_scope_masked_reference_selection`
- control: `V_control_symbolic_positional_scope_masked_reference_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.015073`
  - `rank_correlation = 0.372268`
  - `calibration_slope = 1.098473`
- control:
  - `mae = 0.017790`
  - `rank_correlation = -0.013310`
  - `calibration_slope = -0.610503`

## Interpretation
- The witness beat the bounded symbolic control on both declared mean packet metrics.
- The scope-masked task stayed within the frozen fairness contract.
- The line has earned exactly one next move: retained nuisance hardening with `token_permutation=cdab`.

## Summary CSV
- `logs/ablation_runs/summary/E009_scope_masking_v1.csv`
