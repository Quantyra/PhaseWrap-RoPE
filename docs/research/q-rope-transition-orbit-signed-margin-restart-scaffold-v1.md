# Q-RoPE Transition Orbit Signed-Margin Restart Scaffold v1

Date: 2026-03-11
Stories: S402

## Future Task
- `synthetic_transition_orbit_signed_margin_response`

## Future Candidate
- `V_future_relational_witness_transition_orbit_signed_margin`

## Fixed Future Controls
- `V_control_symbolic_transition_signed_margin_lookup`
- `V_control_symbolic_transition_signed_margin_cross_direction`
- `V_control_symbolic_transition_signed_margin_quadratic`
- `V_control_symbolic_transition_signed_margin_orbit_permuted`

## Fixed First Packet
- seeds: `42`, `123`, `777`
- backend: `sim_quantum_statevector`
- local-only
- zero-credit

## Primary Metrics
- mean absolute error
- sign agreement accuracy

## Hard Stop Contract
- do not approve implementation until the task proves:
  - `coarse_signed_margin_lookup_near_null_pass = true`
  - `within_state_signed_margin_variation_pass = true`
  - `signed_margin_balance_pass = true`
  - `token_view_balance_pass = true`

## Explicitly Disallowed
- reopening the failed unsigned order-margin task
- adding new symbolic control families beyond the fixed four
- remote execution
- benchmark expansion
