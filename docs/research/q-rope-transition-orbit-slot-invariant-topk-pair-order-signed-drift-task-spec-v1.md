# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Drift Task Spec v1

Date: 2026-03-11
Status: memo-only
Story: S572

## Task
- future task: `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response`

## Target
- regress the signed drift of the preferred top-k pair ordering across bounded perturbation contexts under slot-invariant rendering
- keep slot identity a nuisance variable by construction
- keep coarse shortcut structure near-null by construction

## Required Generator Properties
- `latent_slot_invariance_pass = true`
- `latent_slot_max_abs_delta = 0`
- `slot_view_balance_pass = true`
- `coarse_slot_topk_pair_signed_drift_lookup_near_null_pass = true`
- `within_state_topk_pair_signed_drift_variation_pass = true`

## Rationale
- the stopped top-k pair-order drift branch preserved lower error than bounded controls but failed on directional structure
- the next coherent continuation is to make signed drift primary instead of unsigned pair-order drift magnitude
- this is materially different from the stopped branch, not a relabel of the same target
