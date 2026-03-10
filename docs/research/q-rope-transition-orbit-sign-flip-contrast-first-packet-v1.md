# Q-RoPE Transition Orbit Sign-Flip Contrast First Packet v1

Date: 2026-03-11
Stories: S434

## Packet
- task: `synthetic_transition_orbit_sign_flip_contrast_binary`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- candidate:
  - `V_future_relational_witness_transition_orbit_sign_flip_contrast`
- controls:
  - `V_control_symbolic_transition_flip_lookup`
  - `V_control_symbolic_transition_flip_cross_direction`
  - `V_control_symbolic_transition_flip_quadratic`
  - `V_control_symbolic_transition_flip_orbit_permuted`

## Generator Outcome
- hard-stop diagnostics passed on all three seeds
- the packet is valid for interpretation

## Mean Metrics
- witness:
  - accuracy: `0.727273`
  - F1: `0.839961`
- lookup:
  - accuracy: `1.000000`
  - F1: `1.000000`
- cross-direction:
  - accuracy: `0.787879`
  - F1: `0.873294`
- quadratic:
  - accuracy: `0.787879`
  - F1: `0.873294`
- orbit-permuted:
  - accuracy: `0.848485`
  - F1: `0.914035`

## Readout
- the witness did not lead the fixed control stack on either primary metric
- the bounded symbolic lookup control solved the task outright
- this confirms the line is not a useful continuation of the stopped sign-consistency branch
