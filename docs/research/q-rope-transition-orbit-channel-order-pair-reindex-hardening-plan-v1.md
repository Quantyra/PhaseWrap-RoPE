# Q-RoPE Transition Orbit Channel-Order Pair-Reindex Hardening Plan v1

Date: 2026-03-10
Stories: S463

## Next Bounded Step
- rerun the channel-order packet with `pair_reindex=1`
- keep the witness fixed
- keep only the strongest retained controls fixed:
  - `V_control_symbolic_transition_channel_order_orbit_permuted`
  - `V_control_symbolic_transition_channel_order_cross_direction`

## Reason
- `pair_reindex=1` is the smallest non-inert perturbation that changes concrete within-state pairings without widening the task family
- token renaming is likely low-value here because the current branch is already token-balanced by construction
