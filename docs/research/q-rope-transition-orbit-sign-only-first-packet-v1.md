# Q-RoPE Transition Orbit Sign-Only First Packet v1

Date: 2026-03-11
Stories: S416

## Packet
- task: `synthetic_transition_orbit_sign_only_binary`
- candidate: `V_future_relational_witness_transition_orbit_sign_only`
- controls:
  - `V_control_symbolic_transition_sign_lookup`
  - `V_control_symbolic_transition_sign_cross_direction`
  - `V_control_symbolic_transition_sign_quadratic`
  - `V_control_symbolic_transition_sign_orbit_permuted`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Generator Gate
- `coarse_sign_lookup_near_null_pass = true`
- `within_state_sign_variation_pass = true`
- `sign_label_balance_pass = true`
- `token_view_balance_pass = true`

## Mean Metrics
- witness:
  - accuracy `0.848485`
  - F1 `0.913725`
- lookup:
  - accuracy `0.848485`
  - F1 `0.917460`
- cross-direction:
  - accuracy `0.848485`
  - F1 `0.917460`
- quadratic:
  - accuracy `0.848485`
  - F1 `0.917460`
- orbit-permuted:
  - accuracy `0.818182`
  - F1 `0.898162`

## Interpretation
- the witness did not lead the fixed control stack on either classification metric
- the best symbolic controls matched witness accuracy and exceeded witness F1
- this packet does not support branch continuation under the active gate
