# Q-RoPE Transition Orbit Sign-Only Implementation Approval Gate v1

Date: 2026-03-11
Stories: S413

## Decision
- approve one strictly bounded implementation phase

## Approved Scope
- task: `synthetic_transition_orbit_sign_only_binary`
- candidate: `V_future_relational_witness_transition_orbit_sign_only`
- controls:
  - `V_control_symbolic_transition_sign_lookup`
  - `V_control_symbolic_transition_sign_cross_direction`
  - `V_control_symbolic_transition_sign_quadratic`
  - `V_control_symbolic_transition_sign_orbit_permuted`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit

## Hard Stop Rule
- do not interpret the packet if the generator fails to prove:
  - `coarse_sign_lookup_near_null_pass`
  - `within_state_sign_variation_pass`
  - `sign_label_balance_pass`
  - `token_view_balance_pass`

## Explicitly Disallowed
- reopening the failed signed-margin task
- remote execution
- benchmark expansion
- new symbolic control families
- second witness candidate
- packet expansion beyond the fixed first run
