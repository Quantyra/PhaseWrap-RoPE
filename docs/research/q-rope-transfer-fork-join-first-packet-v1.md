# Q-RoPE Transfer Fork-Join First Packet v1

Date: 2026-03-12
Stories: S916

## Packet
- task:
  - `synthetic_symbolic_insufficiency_fork_join_response`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- compared:
  - `V_future_relational_witness_symbolic_insufficiency_fork_join`
  - `V_control_symbolic_symbolic_insufficiency_fork_join_regressor`

## Mean Results
- witness:
  - `mae = 0.073015`
  - `rank_correlation = 0.494591`
  - `calibration_slope = 0.773591`
- control:
  - `mae = 0.104693`
  - `rank_correlation = 0.043194`
  - `calibration_slope = 0.201808`

## Per-Seed Result
- seed `42`
  - witness: `mae 0.072578`, `rank_correlation 0.941176`
  - control: `mae 0.075370`, `rank_correlation 0.305882`
- seed `123`
  - witness: `mae 0.101399`, `rank_correlation 0.195732`
  - control: `mae 0.170028`, `rank_correlation 0.220751`
- seed `777`
  - witness: `mae 0.045069`, `rank_correlation 0.346866`
  - control: `mae 0.068682`, `rank_correlation -0.397051`

## Generator Status
- `coarse_fork_state_null_pass = true`
- `within_fork_state_variation_pass = true`
- `latent_fork_diversity_pass = true`
- `branch_balance_pass = true`
- `rejoin_target_nontrivial_pass = true`
- `token_view_balance_pass = true`

## Audit Status
- witness:
  - `bounded_feature_audit_pass = true`
  - `forbidden_feature_family_absent_pass = true`
- control:
  - `allowed_fork_symbolic_basis_frozen_pass = true`
  - `forbidden_feature_family_absent_pass = true`

## Artifact
- summary:
  - `logs/ablation_runs/summary/transfer_fork_join_v1.csv`
