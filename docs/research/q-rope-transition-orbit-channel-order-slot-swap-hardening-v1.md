# Q-RoPE Transition Orbit Channel-Order Slot-Swap Hardening v1

Date: 2026-03-10
Stories: S470

## Fixed Packet
- dataset: `synthetic_transition_orbit_channel_order_response`
- perturbation: `slot_swap=1`
- retained models:
  - `V_future_relational_witness_transition_orbit_channel_order`
  - `V_control_symbolic_transition_channel_order_cross_direction`
  - `V_control_symbolic_transition_channel_order_orbit_permuted`
- seeds: `42`, `123`, `777`

## Packet Means
- witness:
  - accuracy `0.428571`
  - F1 `0.259259`
- cross-direction:
  - accuracy `0.420635`
  - F1 `0.412698`
- orbit-permuted:
  - accuracy `0.476190`
  - F1 `0.434921`

## Diagnostic Read
- all retained runs recorded `slot_swap=1`
- the packet was not inert
- the witness lost to `V_control_symbolic_transition_channel_order_orbit_permuted` on both primary metrics
- the witness also lost to `V_control_symbolic_transition_channel_order_cross_direction` on F1
