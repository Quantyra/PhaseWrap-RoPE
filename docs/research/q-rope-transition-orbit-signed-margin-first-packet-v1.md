# Q-RoPE Transition Orbit Signed-Margin First Packet v1

Date: 2026-03-11
Stories: S407

## Packet
- task: `synthetic_transition_orbit_signed_margin_response`
- candidate: `V_future_relational_witness_transition_orbit_signed_margin`
- controls:
  - `V_control_symbolic_transition_signed_margin_lookup`
  - `V_control_symbolic_transition_signed_margin_cross_direction`
  - `V_control_symbolic_transition_signed_margin_quadratic`
  - `V_control_symbolic_transition_signed_margin_orbit_permuted`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Generator Gate
- `coarse_signed_margin_lookup_near_null_pass = true`
- `within_state_signed_margin_variation_pass = true`
- `signed_margin_balance_pass = true`
- `token_view_balance_pass = true`

## Mean Metrics
- witness:
  - MAE `0.096415`
  - sign agreement accuracy `0.363636`
  - calibration slope `0.581135`
- lookup:
  - MAE `0.095758`
  - sign agreement accuracy `0.000000`
- cross-direction:
  - MAE `0.096949`
  - sign agreement accuracy `0.060606`
- quadratic:
  - MAE `0.096039`
  - sign agreement accuracy `0.090909`
- orbit-permuted:
  - MAE `0.098690`
  - sign agreement accuracy `0.000000`

## Interpretation
- the witness led on the directional metric
- the witness did not lead on MAE
- this is a mixed packet, not a clean branch survival under the active gate
