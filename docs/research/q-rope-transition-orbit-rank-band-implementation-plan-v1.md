# Transition Orbit Rank-Band Implementation Plan v1

## Writable scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Required generator outputs
- `coarse_rank_lookup_near_null_pass`
- `within_state_rank_band_count_min`
- `rank_band_balance_pass`
- per-state band counts
- bounded summary proving ordinal bands exist inside each coarse orbit-transition state

## Fixed first packet
- dataset: `synthetic_transition_orbit_rank_band_response`
- candidate: `V_future_relational_witness_transition_orbit_rank`
- controls:
  - `V_control_symbolic_transition_orbit_rank_lookup`
  - `V_control_symbolic_transition_cross_direction_regressor`
  - `V_control_symbolic_transition_quadratic_regressor`
  - `V_control_symbolic_transition_orbit_permuted_regressor`
- seeds: `42`, `123`, `777`

## Branch metrics
- primary: rank correlation
- secondary:
  - MAE
  - calibration slope
