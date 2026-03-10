# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Drift Task Spec v1

Date: 2026-03-11
Status: memo-only
Story: S563

## Task
- future task: `synthetic_transition_orbit_slot_invariant_topk_pair_order_drift_response`

## Target
- regress the signed drift magnitude of the preferred top-k pair ordering across bounded perturbation contexts under slot-invariant rendering
- keep slot identity a nuisance variable by construction
- keep coarse shortcut structure near-null by construction

## Required Generator Properties
- `latent_slot_invariance_pass = true`
- `latent_slot_max_abs_delta = 0`
- `slot_view_balance_pass = true`
- `coarse_slot_topk_pair_drift_lookup_near_null_pass = true`
- `within_state_topk_pair_drift_variation_pass = true`

## Rationale
- the stopped slot-invariant top-k pair-order stability branch was too easy for bounded symbolic order controls
- the next coherent continuation is to model drift magnitude under bounded perturbation contexts instead of binary stability classification
- this is materially different from the stopped branch, not a relabel of the same target
