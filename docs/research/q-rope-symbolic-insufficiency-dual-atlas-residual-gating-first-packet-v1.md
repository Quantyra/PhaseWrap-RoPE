# Q-RoPE Symbolic Insufficiency Dual-Atlas Residual-Gating First Packet v1

Date: 2026-03-11
Stories: S740

## Packet
- task: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- witness benchmark:
  - `V_future_relational_witness_symbolic_insufficiency`
- challenger control:
  - `V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_residual`

## Mean Results
- witness:
  - `mae = 0.119724`
  - `rank_correlation = 0.967399`
  - `calibration_slope = 0.989697`
- dual-atlas residual-gating control:
  - `mae = 0.300159`
  - `rank_correlation = 0.189651`
  - `calibration_slope = 0.126391`

## Audit Status
- witness forbidden-feature audit passed on all runs
- dual-atlas residual-gating frozen-family diagnostics passed on all runs:
  - `source_atlas_chart_count_frozen_pass = true`
  - `destination_atlas_chart_count_frozen_pass = true`
  - `atlas_chart_rule_global_pass = true`
  - `atlas_hidden_lookup_absent_pass = true`
  - `dual_atlas_coupling_family_frozen_pass = true`
  - `dual_atlas_residual_family_frozen_pass = true`
  - `dual_atlas_hidden_lookup_absent_pass = true`
  - `allowed_symbolic_basis_frozen_pass = true`
  - `forbidden_feature_family_absent_pass = true`

## Artifacts
- summary csv:
  - `logs/ablation_runs/summary/symbolic_insufficiency_dual_atlas_residual_v1.csv`
