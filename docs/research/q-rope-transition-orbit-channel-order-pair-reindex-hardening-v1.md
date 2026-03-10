# Q-RoPE Transition Orbit Channel-Order Pair-Reindex Hardening v1

Date: 2026-03-10
Stories: S464

## Packet
- dataset: `synthetic_transition_orbit_channel_order_response`
- perturbation: `pair_reindex=1`
- retained models:
  - `V_future_relational_witness_transition_orbit_channel_order`
  - `V_control_symbolic_transition_channel_order_cross_direction`
  - `V_control_symbolic_transition_channel_order_orbit_permuted`

## Means
- witness:
  - mean accuracy `0.533333`
  - mean F1 `0.579365`
- cross-direction:
  - mean accuracy `0.466667`
  - mean F1 `0.488889`
- orbit-permuted:
  - mean accuracy `0.533333`
  - mean F1 `0.577778`

## Readout
- the packet passed all declared generator hard-stop diagnostics
- the retained-model means matched the base packet exactly
- this perturbation did not add new robustness evidence for the branch
