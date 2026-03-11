# Q-RoPE Symbolic Insufficiency Dual-Atlas Residual-Gating Implementation Plan v1

Date: 2026-03-11
Stories: S737

## Writable Scope
- `src/qrope/run.py`
- focused tests only:
  - `tests/test_run_real_mode.py`
- no task-generator changes
- no witness changes
- no control-family proliferation

## Future Challenger
- `V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_residual`

## Frozen Source Charts
- exactly 4 global source charts from:
  - `sector_magnitude_delta >= 0`
  - `ordered_content_delta >= 0`

## Frozen Destination Charts
- exactly 4 global destination charts from:
  - `sector_magnitude_delta >= 0`
  - `orientation_delta >= 0`

## Frozen Coupling Lattice
- exactly 16 source-destination cells:
  - `00->00` through `11->11`
- no cell pruning after packet inspection
- no lattice expansion beyond the fixed 16 cells

## Frozen Base Interaction Set
For each allowed cell, permit exactly:
- `cell x sector_magnitude_delta`
- `cell x ordered_content_delta`
- `cell x orientation_delta`

## Frozen Residual-Gating Set
For each allowed cell, permit exactly:
- `cell x orientation_minus_content`
- `cell x orientation_plus_content`

No other residual or cell-wise interaction terms are allowed.

## Frozen Residual Definitions
- `orientation_minus_content = orientation_delta - ordered_content_delta`
- `orientation_plus_content = orientation_delta + ordered_content_delta`
- both must be derived only from already declared analog summaries

## Required Diagnostics
- `source_atlas_chart_count_frozen_pass`
- `destination_atlas_chart_count_frozen_pass`
- `atlas_chart_rule_global_pass`
- `atlas_hidden_lookup_absent_pass`
- `dual_atlas_coupling_family_frozen_pass`
- `dual_atlas_residual_family_frozen_pass`
- `dual_atlas_hidden_lookup_absent_pass`
- `allowed_symbolic_basis_frozen_pass`
- `forbidden_feature_family_absent_pass`

## Future Packet
- task:
  - `synthetic_symbolic_insufficiency_transition_response`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- models:
  - `V_future_relational_witness_symbolic_insufficiency`
  - `V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_residual`

## Stop Rule
- stop immediately if the dual-atlas residual-gating control matches or beats the witness on both declared packet metrics
