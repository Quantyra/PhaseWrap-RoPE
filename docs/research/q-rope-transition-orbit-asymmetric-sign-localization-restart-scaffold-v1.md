# Q-RoPE Transition Orbit Asymmetric Sign-Localization Restart Scaffold v1

Date: 2026-03-11
Stories: S438

## Future Task
- `synthetic_transition_orbit_asymmetric_sign_localization_binary`

## Future Candidate
- `V_future_relational_witness_transition_orbit_asymmetric_sign_localization`

## Fixed Future Controls
- `V_control_symbolic_transition_localization_lookup`
- `V_control_symbolic_transition_localization_cross_direction`
- `V_control_symbolic_transition_localization_quadratic`
- `V_control_symbolic_transition_localization_orbit_permuted`

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
  - `coarse_localization_lookup_near_null_pass = true`
  - `within_state_localization_variation_pass = true`
  - `paired_channel_diversity_pass = true`
  - `localization_label_balance_pass = true`
  - `token_view_balance_pass = true`

## Explicitly Disallowed
- reopening the failed sign-flip contrast task
- remote execution
- benchmark expansion
- new symbolic control families
- second witness candidate
