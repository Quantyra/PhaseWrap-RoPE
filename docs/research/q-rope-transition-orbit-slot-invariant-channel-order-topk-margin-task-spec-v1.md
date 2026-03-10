# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Margin Task Spec v1

Date: 2026-03-10
Stories: S509

## Task
- future task: `synthetic_transition_orbit_slot_invariant_channel_order_topk_margin_response`

## Objective
- supervise the signed separation margin between the top-k subset and the remaining candidates under slot-invariant ordered transition structure
- keep slot identity a nuisance variable by construction
- avoid the zero-positive collapse seen in the stopped top-k consistency branch

## Generator Contract
- latent slot invariance must hold exactly
- coarse top-k margin lookup must be near-null
- within-state top-k margin variation must be present
- slot-view balance must hold

## Primary Metrics
- `mae`
- `rank_correlation`

## Rejection Rule
- reject any continuation that falls back to the same binary consistency target or reintroduces full-list ranking as the primary objective
