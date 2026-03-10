# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Margin Task Spec v1

Date: 2026-03-10
Stories: S482

## Task
- `synthetic_transition_orbit_slot_invariant_channel_order_margin_response`

## Target
- predict the signed separation margin between the strongest and second-strongest slot-invariant channel-order responses
- the supervised target must be computed from a latent slot-symmetric construction
- swapping rendered observation slots must leave the latent target unchanged

## Generator Contract
- latent state is sampled first
- target is derived from a slot-symmetric latent margin, not from rendered slot position
- diagnostics must prove:
  - `latent_slot_invariance_pass = true`
  - `latent_slot_max_abs_delta = 0`
  - `slot_view_balance_pass = true`
  - `coarse_slot_margin_lookup_near_null_pass = true`
  - `within_state_margin_variation_pass = true`

## Rejection Rule
- reject the task if any paired slot-swapped render changes the latent target
- reject the task if coarse slot-state lookup alone recovers the margin structure
