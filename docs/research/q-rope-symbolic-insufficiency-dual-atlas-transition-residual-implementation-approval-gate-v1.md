# Q-RoPE Symbolic Insufficiency Dual-Atlas Transition-Residual Implementation Approval Gate v1

Date: 2026-03-11
Stories: S755

## Decision
- approve one bounded implementation-planning step only
- do not approve execution in this step

## Frozen Task
- `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds:
  - `42`
  - `123`
  - `777`

## Standing Baseline
- witness benchmark:
  - `V_future_relational_witness_symbolic_insufficiency`

## Future Challenger
- `V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_residual`

## Frozen Dual-Atlas Transition-Residual Contract
- source-chart count fixed at `4`
- destination-chart count fixed at `4`
- source-chart rule fixed from:
  - `sector_magnitude_delta >= 0`
  - `ordered_content_delta >= 0`
- destination-chart rule fixed from:
  - `sector_magnitude_delta >= 0`
  - `orientation_delta >= 0`
- both chart rules are global and sample-independent
- coupling lattice:
  - exactly `4 x 4`
- allowed base cell interactions:
  - lattice-cell indicator x `sector_magnitude_delta`
  - lattice-cell indicator x `ordered_content_delta`
  - lattice-cell indicator x `orientation_delta`
- allowed residual-gating interactions only:
  - lattice-cell indicator x `orientation_minus_content`
  - lattice-cell indicator x `orientation_plus_content`
- allowed bilinear residual interactions only:
  - lattice-cell indicator x `sector_times_orientation_minus_content`
  - lattice-cell indicator x `sector_times_orientation_plus_content`
- allowed transition-residual interactions only:
  - lattice-cell indicator x `source_to_dest_orientation_minus_content`
  - lattice-cell indicator x `dest_to_source_orientation_minus_content`
- frozen residual definitions:
  - `orientation_minus_content = orientation_delta - ordered_content_delta`
  - `orientation_plus_content = orientation_delta + ordered_content_delta`
- frozen bilinear definitions:
  - `sector_times_orientation_minus_content = sector_magnitude_delta * orientation_minus_content`
  - `sector_times_orientation_plus_content = sector_magnitude_delta * orientation_plus_content`
- frozen transition-residual definitions:
  - `source_sign = +1` iff source chart is in `{10,11}`, else `-1`
  - `dest_sign = +1` iff destination chart is in `{10,11}`, else `-1`
  - `source_to_dest_orientation_minus_content = source_sign * orientation_minus_content`
  - `dest_to_source_orientation_minus_content = dest_sign * orientation_minus_content`
- no other residual, bilinear, or cell-wise interaction terms are allowed

## Required Future Audits
- `source_atlas_chart_count_frozen_pass`
- `destination_atlas_chart_count_frozen_pass`
- `atlas_chart_rule_global_pass`
- `atlas_hidden_lookup_absent_pass`
- `dual_atlas_coupling_family_frozen_pass`
- `dual_atlas_residual_family_frozen_pass`
- `dual_atlas_bilinear_family_frozen_pass`
- `dual_atlas_transition_residual_family_frozen_pass`
- `dual_atlas_hidden_lookup_absent_pass`
- `allowed_symbolic_basis_frozen_pass`
- `forbidden_feature_family_absent_pass`

## Forbidden Feature Family
- latent path ids
- exact microstate keys
- hidden tuple lookups
- per-example chart refinement
- source or destination chart count growth beyond `4`
- lattice growth beyond `4 x 4`
- per-cell bespoke nonlinear transforms
- any transition-residual channel beyond the two frozen definitions
- uncontrolled basis growth after packet inspection

## Hard Stop Rule
Do not reopen code unless the future implementation plan can state, in advance:
- exact lattice size
- exact source chart rule
- exact destination chart rule
- exact base cell-analog interaction set
- exact residual-gating interaction set
- exact bilinear interaction set
- exact transition-residual interaction set
- exact residual, bilinear, and transition-residual definitions
- exact diagnostic names emitted in `run_diagnostics`
