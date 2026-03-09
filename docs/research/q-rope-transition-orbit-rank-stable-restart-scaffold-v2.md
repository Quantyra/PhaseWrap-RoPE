# Transition Orbit Rank-Stable Restart Scaffold v2

## Future candidate
- `V_future_relational_witness_transition_orbit_rank`

## Fixed future controls
- `V_control_symbolic_transition_orbit_rank_lookup`
- `V_control_symbolic_transition_cross_direction_regressor`
- `V_control_symbolic_transition_quadratic_regressor`
- `V_control_symbolic_transition_orbit_permuted_regressor`

## Fixed first packet
- local-only
- zero-credit
- dataset: `synthetic_transition_orbit_rank_band_response`
- seeds: `42`, `123`, `777`
- primary metric: rank correlation
- secondary metrics:
  - MAE
  - calibration slope

## Approval precondition
- task diagnostics must prove coarse lookup near-null within each coarse orbit-transition state family
