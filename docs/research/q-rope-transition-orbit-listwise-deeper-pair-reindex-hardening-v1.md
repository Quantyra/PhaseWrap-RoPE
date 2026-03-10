# Q-RoPE Transition Orbit Listwise Deeper Pair-Reindex Hardening v1

Date: 2026-03-11
Stories: S389

## Packet
- task: `synthetic_transition_orbit_listwise_ranking`
- perturbation: `pair_reindex = 7`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- candidate: `V_future_relational_witness_transition_orbit_listwise`
- controls:
  - `V_control_symbolic_transition_list_cross_direction`
  - `V_control_symbolic_transition_list_orbit_permuted`

## Mean Results
- witness: accuracy `0.121212`, order-F1 `0.419913`, eval loss `0.337705`
- cross-direction: accuracy `0.272727`, order-F1 `0.361039`, eval loss `0.329962`
- orbit-permuted: accuracy `0.272727`, order-F1 `0.373160`, eval loss `0.327803`

## Interpretation
- This perturbation was non-inert and stronger than `pair_reindex = 1`.
- The witness kept the higher order-F1.
- But it lost the primary listwise metric, top-1 accuracy, to both retained symbolic controls.
- That is a clean branch failure under the active hardening rule.
