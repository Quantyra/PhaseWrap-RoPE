# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Stability Task Spec v1

Date: 2026-03-10
Status: memo-only
Story: S554

## Task
- future task: `synthetic_transition_orbit_slot_invariant_topk_pair_order_stability_binary`

## Target
- classify whether the preferred top-k pair ordering remains stable across bounded perturbation contexts under slot-invariant rendering
- keep slot identity a nuisance variable by construction
- keep coarse shortcut structure near-null by construction

## Required Generator Properties
- `latent_slot_invariance_pass = true`
- `latent_slot_max_abs_delta = 0`
- `slot_view_balance_pass = true`
- `coarse_slot_topk_pair_stability_lookup_near_null_pass = true`
- `within_state_topk_pair_stability_variation_pass = true`

## Rationale
- the stopped slot-invariant top-k pair-order agreement branch was too easy for bounded symbolic order controls
- the next coherent continuation is to test order stability across bounded perturbation contexts instead of direct pair-order agreement
- this is materially different from the stopped branch, not a relabel of the same target
