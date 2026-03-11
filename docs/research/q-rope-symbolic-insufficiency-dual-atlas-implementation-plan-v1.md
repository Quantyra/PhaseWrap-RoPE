# Q-RoPE Symbolic Insufficiency Dual-Atlas Implementation Plan v1

Date: 2026-03-11
Stories: S727

## Writable Scope
- `src/qrope/run.py`
- focused tests only:
  - `tests/test_run_real_mode.py`
- no task-generator changes
- no witness changes
- no control-family proliferation

## Future Challenger
- `V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas`

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
- no expansion beyond the fixed 16 cells

## Frozen Coupling Interaction Set
For each allowed cell, permit exactly:
- `cell x sector_magnitude_delta`
- `cell x ordered_content_delta`
- `cell x orientation_delta`

No other cell interactions are allowed.

## Required Diagnostics
- `source_atlas_chart_count_frozen_pass`
- `destination_atlas_chart_count_frozen_pass`
- `atlas_chart_rule_global_pass`
- `atlas_hidden_lookup_absent_pass`
- `dual_atlas_coupling_family_frozen_pass`
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
  - `V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas`

## Stop Rule
- stop immediately if the dual-atlas control matches or beats the witness on both declared packet metrics
