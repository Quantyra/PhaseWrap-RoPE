# Q-RoPE Transition Orbit Listwise Ranking First Packet v1

Date: 2026-03-11
Stories: S379-S380

## Packet
- task: `synthetic_transition_orbit_listwise_ranking`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- candidate: `V_future_relational_witness_transition_orbit_listwise`
- controls:
  - `V_control_symbolic_transition_list_lookup`
  - `V_control_symbolic_transition_list_cross_direction`
  - `V_control_symbolic_transition_list_quadratic`
  - `V_control_symbolic_transition_list_orbit_permuted`

## Mean Results
- witness: accuracy `0.303030`, order-F1 `0.464574`, eval loss `0.337273`
- lookup: accuracy `0.000000`, order-F1 `0.000000`, eval loss `0.333333`
- cross-direction: accuracy `0.303030`, order-F1 `0.329005`, eval loss `0.329682`
- quadratic: accuracy `0.242424`, order-F1 `0.338095`, eval loss `0.331225`
- orbit-permuted: accuracy `0.303030`, order-F1 `0.350217`, eval loss `0.328269`

## Interpretation
- The witness did not produce a clean primary-metric sweep.
- It tied the strongest symbolic controls on top-1 accuracy.
- It led the full control stack on the secondary listwise metric, order-F1.
- This is a survive-but-not-settle result rather than a clean win or a clean stop.
