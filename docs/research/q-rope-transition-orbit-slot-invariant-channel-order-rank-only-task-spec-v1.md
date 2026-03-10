# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Rank-Only Task Spec v1

Date: 2026-03-10
Stories: S491

## Task
- future task: `synthetic_transition_orbit_slot_invariant_channel_order_rank_only`

## Objective
- supervise rank structure directly under slot-invariant ordered transition states
- remove the mixed magnitude target from the stopped margin branch
- keep slot identity a nuisance variable by construction

## Generator Contract
- latent slot invariance must hold exactly
- coarse rank-only lookup must be near-null
- within-state rank variation must be present
- slot-view balance must hold

## Primary Metrics
- `accuracy`
- `order_f1`

## Rejection Rule
- reject any continuation that reintroduces raw margin magnitude as a primary target
