# Q-RoPE Transition Orbit Sign-Consistency First Packet v1

Date: 2026-03-11
Stories: S425

## Packet
- task: `synthetic_transition_orbit_sign_consistency_binary`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- candidate:
  - `V_future_relational_witness_transition_orbit_sign_consistency`
- controls:
  - `V_control_symbolic_transition_consistency_lookup`
  - `V_control_symbolic_transition_consistency_cross_direction`
  - `V_control_symbolic_transition_consistency_quadratic`
  - `V_control_symbolic_transition_consistency_orbit_permuted`

## Generator Outcome
- hard-stop diagnostics passed on all three seeds
- the packet is valid for interpretation

## Mean Metrics
- witness:
  - accuracy: `0.696970`
  - F1: `0.000000`
- lookup:
  - accuracy: `0.000000`
  - F1: `0.000000`
- cross-direction:
  - accuracy: `0.787879`
  - F1: `0.000000`
- quadratic:
  - accuracy: `0.787879`
  - F1: `0.000000`
- orbit-permuted:
  - accuracy: `0.787879`
  - F1: `0.000000`

## Readout
- the witness did not lead the fixed control stack on either primary metric
- all models collapsed to zero positive-class F1, so the branch did not recover usable directional-consistency classification
