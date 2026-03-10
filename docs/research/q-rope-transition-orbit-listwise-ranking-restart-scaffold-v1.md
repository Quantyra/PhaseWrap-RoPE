# Q-RoPE Transition Orbit Listwise Ranking Restart Scaffold v1

Date: 2026-03-11
Story: S375

## Future Task
`synthetic_transition_orbit_listwise_ranking`

## Future Candidate
`V_future_relational_witness_transition_orbit_listwise`

## Fixed Future Controls
- `V_control_symbolic_transition_list_lookup`
- `V_control_symbolic_transition_list_cross_direction`
- `V_control_symbolic_transition_list_quadratic`
- `V_control_symbolic_transition_list_orbit_permuted`

## Fixed First Packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit

## Primary Metrics
- top-1 listwise accuracy
- mean Kendall-style rank agreement or equivalent ordinal ranking score

## Required Generator Diagnostics
- `coarse_list_lookup_near_null_pass = true`
- `within_state_list_count_min >= 2`
- `rank_position_balance_pass = true`
- `token_view_balance_pass = true`

## Hard Stop Rule
Do not reopen implementation unless the generator proves that the ranking target varies entirely within the same coarse transition state and cannot be reduced to a coarse-state list lookup.
