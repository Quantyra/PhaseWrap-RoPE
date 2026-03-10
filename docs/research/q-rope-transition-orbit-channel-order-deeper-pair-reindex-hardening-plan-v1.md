# Q-RoPE Transition Orbit Channel-Order Deeper Pair-Reindex Hardening Plan v1

Date: 2026-03-10
Stories: S466

## Next Bounded Step
- rerun the active channel-order branch with `pair_reindex=7`
- keep the witness fixed
- keep only the retained strongest controls fixed:
  - `V_control_symbolic_transition_channel_order_cross_direction`
  - `V_control_symbolic_transition_channel_order_orbit_permuted`

## Reason
- `pair_reindex=1` was effectively inert on this generator
- `pair_reindex=7` is the next bounded perturbation likely to change concrete within-state pairings without widening the task or control family
