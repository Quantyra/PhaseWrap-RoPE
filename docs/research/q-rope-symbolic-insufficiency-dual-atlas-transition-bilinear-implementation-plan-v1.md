# Q-RoPE Symbolic Insufficiency Dual-Atlas Transition-Bilinear Implementation Plan v1

Date: 2026-03-11
Stories: S767

## Objective
Define one bounded implementation cycle for a materially stronger symbolic challenger without relaxing the frozen symbolic-insufficiency fairness contract.

## Challenger
- `V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_bilinear`

## Standing Witness Benchmark
- `V_future_relational_witness_symbolic_insufficiency`

## Frozen Task
- `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds:
  - `42`
  - `123`
  - `777`

## Writable Scope
- `src/qrope/run.py`
- `tests/test_run_real_mode.py`

## Frozen Source/Destination Atlas Contract
- source-chart count fixed at `4`
- destination-chart count fixed at `4`
- source-chart rule uses only:
  - `sector_magnitude_delta >= 0`
  - `ordered_content_delta >= 0`
- destination-chart rule uses only:
  - `sector_magnitude_delta >= 0`
  - `orientation_delta >= 0`
- both chart rules are global and sample-independent
- coupling lattice fixed at `4 x 4`

## Frozen Base Interaction Family
- lattice-cell indicator x `sector_magnitude_delta`
- lattice-cell indicator x `ordered_content_delta`
- lattice-cell indicator x `orientation_delta`

## Frozen Residual Channels
- `orientation_minus_content = orientation_delta - ordered_content_delta`
- `orientation_plus_content = orientation_delta + ordered_content_delta`

## Frozen Bilinear Channels
- `sector_times_orientation_minus_content = sector_magnitude_delta * orientation_minus_content`
- `sector_times_orientation_plus_content = sector_magnitude_delta * orientation_plus_content`

## Frozen Transition-Residual Channels
- `source_sign = +1` iff source chart is in `{10,11}`, else `-1`
- `dest_sign = +1` iff destination chart is in `{10,11}`, else `-1`
- `source_to_dest_orientation_minus_content = source_sign * orientation_minus_content`
- `dest_to_source_orientation_minus_content = dest_sign * orientation_minus_content`

## Frozen Transition-Bilinear Channels
- `source_to_dest_sector_times_orientation_minus_content = source_sign * sector_times_orientation_minus_content`
- `dest_to_source_sector_times_orientation_minus_content = dest_sign * sector_times_orientation_minus_content`

## Allowed Challenger Basis
- all frozen base interaction features
- all frozen residual-gating features from the previous dual-atlas residual family
- all frozen bilinear residual features from the previous dual-atlas bilinear family
- all frozen transition-residual features from the previous dual-atlas transition-residual family
- exactly these additional transition-bilinear features:
  - `cell_ij_kl_source_to_dest_sector_times_orientation_minus_content`
  - `cell_ij_kl_dest_to_source_sector_times_orientation_minus_content`
- no other per-cell feature types are allowed

## Required Audits
- `source_atlas_chart_count_frozen_pass`
- `destination_atlas_chart_count_frozen_pass`
- `atlas_chart_rule_global_pass`
- `atlas_hidden_lookup_absent_pass`
- `dual_atlas_coupling_family_frozen_pass`
- `dual_atlas_residual_family_frozen_pass`
- `dual_atlas_bilinear_family_frozen_pass`
- `dual_atlas_transition_residual_family_frozen_pass`
- `dual_atlas_transition_bilinear_family_frozen_pass`
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
- any transition-bilinear channel beyond the two frozen definitions
- uncontrolled basis growth after packet inspection

## Fixed Packet Rule
Run exactly one packet:
- witness vs dual-atlas transition-bilinear challenger
- seeds `42`, `123`, `777`
- stop the line immediately if the challenger matches or beats the witness on both declared packet metrics

## Declared Packet Metrics
- `mae`
- `rank_correlation`
