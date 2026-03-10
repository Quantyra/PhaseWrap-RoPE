# Q-RoPE Transition Orbit Sign-Flip Contrast Restart Scaffold v1

Date: 2026-03-11
Stories: S429

## Future Task
- `synthetic_transition_orbit_sign_flip_contrast_binary`

## Future Candidate
- `V_future_relational_witness_transition_orbit_sign_flip_contrast`

## Fixed Future Controls
- `V_control_symbolic_transition_flip_lookup`
- `V_control_symbolic_transition_flip_cross_direction`
- `V_control_symbolic_transition_flip_quadratic`
- `V_control_symbolic_transition_flip_orbit_permuted`

## Fixed First Packet
- seeds: `42`, `123`, `777`
- backend: `sim_quantum_statevector`
- local-only
- zero-credit

## Primary Metrics
- accuracy
- F1

## Hard Stop Contract
- do not approve implementation until the task proves:
  - `coarse_flip_lookup_near_null_pass = true`
  - `within_state_flip_variation_pass = true`
  - `paired_context_diversity_pass = true`
  - `flip_label_balance_pass = true`
  - `token_view_balance_pass = true`

## Explicitly Disallowed
- reopening the failed sign-consistency task
- remote execution
- benchmark expansion
- new symbolic control families
- second witness candidate
