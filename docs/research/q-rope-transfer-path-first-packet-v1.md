# Q-RoPE Transfer Path First Packet v1

Date: 2026-03-11
Stories: S857

## Packet
- task:
  - `synthetic_symbolic_insufficiency_path_response`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- compared:
  - `V_future_relational_witness_symbolic_insufficiency_path`
  - `V_control_symbolic_symbolic_insufficiency_path_regressor`

## Mean Results
- witness:
  - `mae = 0.100666`
  - `rank_correlation = 0.501251`
  - `calibration_slope = 0.544921`
- control:
  - `mae = 0.149769`
  - `rank_correlation = -0.390044`
  - `calibration_slope = -0.545625`

## Per-Seed Result
- seed `42`
  - witness: `mae 0.052537`, `rank_correlation 0.313276`
  - control: `mae 0.072670`, `rank_correlation -0.289178`
- seed `123`
  - witness: `mae 0.185118`, `rank_correlation 0.619048`
  - control: `mae 0.257518`, `rank_correlation -0.523810`
- seed `777`
  - witness: `mae 0.064344`, `rank_correlation 0.571429`
  - control: `mae 0.119119`, `rank_correlation -0.357143`

## Generator Status
- `coarse_path_state_null_pass = true`
- `within_path_state_variation_pass = true`
- `latent_path_diversity_pass = true`
- `token_view_balance_pass = true`
- `path_length_balance_pass = true`

## Audit Status
- witness:
  - `bounded_feature_audit_pass = true`
  - `forbidden_feature_family_absent_pass = true`
- control:
  - `allowed_path_symbolic_basis_frozen_pass = true`
  - `forbidden_feature_family_absent_pass = true`

## Artifact
- summary:
  - `logs/ablation_runs/summary/transfer_path_v1.csv`
