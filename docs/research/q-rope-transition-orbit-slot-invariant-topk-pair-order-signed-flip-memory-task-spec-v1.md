# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Flip Memory Task Specification v1

Date: 2026-03-11
Stories: S644

## Task
- `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary`

## Objective
- classify whether the top-k pair-order response preserves directional memory of a signed flip under slot-invariant rendering

## Required Properties
- latent slot identity must remain a nuisance variable
- memory must not collapse to coarse signed-flip lookup
- within-state memory variation must exist
- paired context diversity must be explicit
- label balance must be enforced

## Generator Diagnostics
- `latent_slot_invariance_pass`
- `latent_slot_max_abs_delta = 0`
- `slot_view_balance_pass`
- `coarse_slot_topk_pair_signed_flip_memory_lookup_near_null_pass`
- `within_state_topk_pair_signed_flip_memory_variation_pass`
- `paired_context_diversity_pass`
- `signed_flip_memory_label_balance_pass`

## Status
- memo-only
- no implementation approved
