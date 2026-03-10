# Q-RoPE Transition Orbit Pairwise Order Restart Scaffold v1

Date: 2026-03-11
Story: S366

## Future Task
`synthetic_transition_orbit_pairwise_order_binary`

## Future Candidate
`V_future_relational_witness_transition_orbit_order`

## Fixed Future Controls
- `V_control_symbolic_transition_order_lookup`
- `V_control_symbolic_transition_order_cross_direction`
- `V_control_symbolic_transition_order_quadratic`
- `V_control_symbolic_transition_order_orbit_permuted`

## Fixed First Packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit

## Primary Metrics
- accuracy
- F1
- rank consistency diagnostics only as secondary support

## Required Generator Diagnostics
- `coarse_order_lookup_near_null_pass = true`
- `within_state_pair_count_min >= 2`
- `pair_label_balance_pass = true`
- `token_view_balance_pass = true`

## Hard Stop Rule
Do not reopen implementation if the generator cannot prove the label varies within the same coarse transition state.
