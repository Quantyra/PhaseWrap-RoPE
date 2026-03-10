# Q-RoPE Transition Orbit Channel-Order Slot-Swap Hardening Plan v1

Date: 2026-03-10
Stories: S469

## Next Bounded Step
- rerun the active channel-order branch with `slot_swap=1`
- keep the witness fixed
- keep only the retained strongest controls fixed:
  - `V_control_symbolic_transition_channel_order_cross_direction`
  - `V_control_symbolic_transition_channel_order_orbit_permuted`

## Reason
- pair-reindex perturbations are now exhausted as a useful hardening family on this task
- `slot_swap=1` is the next smallest structural perturbation that changes the dual-sample ordering without widening the task or control family
