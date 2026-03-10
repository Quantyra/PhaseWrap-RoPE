# Q-RoPE Transition Orbit Order Margin Restart Scaffold v1

Date: 2026-03-11
Stories: S393

## Future Candidate
- `V_future_relational_witness_transition_orbit_order_margin`

## Fixed Future Controls
- `V_control_symbolic_transition_margin_lookup`
- `V_control_symbolic_transition_margin_cross_direction`
- `V_control_symbolic_transition_margin_quadratic`
- `V_control_symbolic_transition_margin_orbit_permuted`

## Fixed First Packet
- task: `synthetic_transition_orbit_order_margin_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit

## Primary Metrics
- mean absolute error
- rank correlation

## Hard Stop Diagnostics
- `coarse_margin_lookup_near_null_pass`
- `within_state_margin_variation_pass`
- `top1_only_shortcut_absent`
- `token_view_balance_pass`
