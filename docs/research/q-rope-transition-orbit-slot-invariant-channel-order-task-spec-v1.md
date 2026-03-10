# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Task Spec v1

Date: 2026-03-10
Stories: S473

## Task
- `synthetic_transition_orbit_slot_invariant_channel_order_response`

## Target
- predict relative channel ordering under a construction where swapping observation slots leaves the latent target unchanged
- the supervised signal must be identical across paired slot-swapped renders of the same latent state

## Generator Contract
- latent state is sampled first
- both observation slots are rendered from the same latent transition-orbit state family
- supervised target is computed from the latent state, not from slot position in the rendered sample
- diagnostics must prove:
  - `latent_slot_invariance_pass = true`
  - `latent_slot_max_abs_delta = 0`
  - `slot_view_balance_pass = true`
  - `coarse_slot_order_lookup_near_null_pass = true`

## Rejection Rule
- reject the task if any latent paired render changes the target under slot swap
- reject the task if slot identity alone recovers the target at coarse state level
