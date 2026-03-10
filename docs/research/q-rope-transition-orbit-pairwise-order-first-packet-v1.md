# Q-RoPE Transition Orbit Pairwise Order First Packet v1

Date: 2026-03-11
Stories: S370-S371

## Packet
- task: `synthetic_transition_orbit_pairwise_order_binary`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- candidate: `V_future_relational_witness_transition_orbit_order`
- controls:
  - `V_control_symbolic_transition_order_lookup`
  - `V_control_symbolic_transition_order_cross_direction`
  - `V_control_symbolic_transition_order_quadratic`
  - `V_control_symbolic_transition_order_orbit_permuted`

## Mean Results
- witness: accuracy `0.515151`, F1 `0.250000`, eval loss `0.797182`
- lookup: accuracy `0.454545`, F1 `0.625000`, eval loss `0.730347`
- cross-direction: accuracy `0.636364`, F1 `0.333333`, eval loss `0.645490`
- quadratic: accuracy `0.636364`, F1 `0.333333`, eval loss `0.644777`
- orbit-permuted: accuracy `0.636364`, F1 `0.333333`, eval loss `0.647111`

## Interpretation
- The witness did not lead on either primary classification metric.
- Three bounded symbolic controls tied above it on accuracy.
- The lookup control stayed weaker on accuracy but still exceeded the witness on mean F1.
- This is a clean branch failure under the approved rule.
