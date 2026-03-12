# Q-RoPE Transfer Loop-Closure First Packet v1

Date: 2026-03-11
Stories: S886

## Packet
- task:
  - `synthetic_symbolic_insufficiency_loop_closure_response`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- compared:
  - `V_future_relational_witness_symbolic_insufficiency_loop`
  - `V_control_symbolic_symbolic_insufficiency_loop_regressor`

## Mean Results
- witness:
  - `mae = 0.045198`
  - `rank_correlation = 0.387512`
  - `calibration_slope = 0.667062`
- control:
  - `mae = 0.066617`
  - `rank_correlation = -0.160944`
  - `calibration_slope = -0.316127`

## Per-Seed Result
- seed `42`
  - witness: `mae 0.044305`, `rank_correlation 0.288126`
  - control: `mae 0.053907`, `rank_correlation 0.039457`
- seed `123`
  - witness: `mae 0.049323`, `rank_correlation 0.198588`
  - control: `mae 0.067439`, `rank_correlation -0.509948`
- seed `777`
  - witness: `mae 0.041966`, `rank_correlation 0.675823`
  - control: `mae 0.078506`, `rank_correlation -0.012341`

## Generator Status
- `coarse_loop_state_null_pass = true`
- `within_loop_state_variation_pass = true`
- `latent_loop_diversity_pass = true`
- `token_view_balance_pass = true`
- `loop_length_balance_pass = true`
- `closure_target_nontrivial_pass = true`

## Audit Status
- witness:
  - `bounded_feature_audit_pass = true`
  - `forbidden_feature_family_absent_pass = true`
- control:
  - `allowed_loop_symbolic_basis_frozen_pass = true`
  - `forbidden_feature_family_absent_pass = true`

## Artifact
- summary:
  - `logs/ablation_runs/summary/transfer_loop_v1.csv`
