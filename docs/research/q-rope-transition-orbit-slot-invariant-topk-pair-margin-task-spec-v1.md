# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Margin Task Spec v1

Date: 2026-03-10
Status: memo-only
Story: S536

## Task
- future task: `synthetic_transition_orbit_slot_invariant_topk_pair_margin_response`

## Target
- regress the signed separation margin between the preferred top-k pair relation and its strongest competing pair relation
- keep slot identity a nuisance variable by construction
- keep coarse shortcut structure near-null by construction

## Required Generator Properties
- `latent_slot_invariance_pass = true`
- `latent_slot_max_abs_delta = 0`
- `slot_view_balance_pass = true`
- `coarse_slot_topk_pair_margin_lookup_near_null_pass = true`
- `within_state_topk_pair_margin_variation_pass = true`

## Rationale
- the stopped slot-invariant top-k preference branch failed as a binary objective against bounded controls
- the next coherent continuation is to make pair-margin magnitude primary instead of binary top-k preference
- this is materially different from the stopped branch, not a relabel of the same target
