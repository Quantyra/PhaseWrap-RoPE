# Q-RoPE Transition Orbit Channel-Order First Packet v1

Date: 2026-03-10
Stories: S461

## Packet
- dataset: `synthetic_transition_orbit_channel_order_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- candidate: `V_future_relational_witness_transition_orbit_channel_order`
- controls:
  - `V_control_symbolic_transition_channel_order_lookup`
  - `V_control_symbolic_transition_channel_order_cross_direction`
  - `V_control_symbolic_transition_channel_order_quadratic`
  - `V_control_symbolic_transition_channel_order_orbit_permuted`

## Means
- witness:
  - mean accuracy `0.533333`
  - mean F1 `0.579365`
- lookup:
  - mean accuracy `0.400000`
  - mean F1 `0.571429`
- cross-direction:
  - mean accuracy `0.466667`
  - mean F1 `0.488889`
- quadratic:
  - mean accuracy `0.466667`
  - mean F1 `0.488889`
- orbit-permuted:
  - mean accuracy `0.533333`
  - mean F1 `0.577778`

## Readout
- the witness tied the strongest retained control on mean accuracy
- the witness led the full stack on mean F1
- all generator hard-stop diagnostics passed on all packet runs

## Artifact
- summary: `logs/ablation_runs/summary/transition_orbit_channel_order_v1.csv`
