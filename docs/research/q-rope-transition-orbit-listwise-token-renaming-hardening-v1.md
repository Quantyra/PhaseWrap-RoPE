# Q-RoPE Transition Orbit Listwise Token-Renaming Hardening v1

Date: 2026-03-11
Stories: S383

## Packet
- task: `synthetic_transition_orbit_listwise_ranking`
- perturbation: `token_permutation = cdab`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- candidate: `V_future_relational_witness_transition_orbit_listwise`
- controls:
  - `V_control_symbolic_transition_list_cross_direction`
  - `V_control_symbolic_transition_list_orbit_permuted`

## Mean Results
- witness: accuracy `0.303030`, order-F1 `0.464574`, eval loss `0.337273`
- cross-direction: accuracy `0.303030`, order-F1 `0.329005`, eval loss `0.329682`
- orbit-permuted: accuracy `0.303030`, order-F1 `0.350217`, eval loss `0.328269`

## Interpretation
- The renamed packet matches the base listwise packet exactly.
- Under the current orbit-canonical rendering, `token_permutation = cdab` is inert for this task.
- This packet does not count as new robustness evidence.
