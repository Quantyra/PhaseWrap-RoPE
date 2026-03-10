# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Agreement Task Spec v1

Date: 2026-03-10
Status: memo-only
Story: S545

## Task
- future task: `synthetic_transition_orbit_slot_invariant_topk_pair_order_agreement_binary`

## Target
- classify whether the preferred top-k pair ordering agrees across the paired slot-invariant views
- keep slot identity a nuisance variable by construction
- keep coarse shortcut structure near-null by construction

## Required Generator Properties
- `latent_slot_invariance_pass = true`
- `latent_slot_max_abs_delta = 0`
- `slot_view_balance_pass = true`
- `coarse_slot_topk_pair_order_lookup_near_null_pass = true`
- `within_state_topk_pair_order_variation_pass = true`

## Rationale
- the stopped slot-invariant top-k pair-margin branch preserved lower error than bounded controls but failed on rank structure
- the next coherent continuation is to test pair-order agreement directly instead of pair-margin magnitude
- this is materially different from the stopped branch, not a relabel of the same target
