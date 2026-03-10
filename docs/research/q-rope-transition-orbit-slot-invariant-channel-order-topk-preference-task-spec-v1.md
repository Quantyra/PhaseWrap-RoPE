# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Preference Task Spec v1

Date: 2026-03-10
Status: memo-only
Story: S527

## Task
- task id: `synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary`
- supervision type: binary preference over the relative order of the top-k candidate subset

## Design Goal
- make top-k pairwise preference primary
- remove full-list rank reconstruction from the supervised target
- preserve latent slot invariance by construction

## Required Generator Properties
- `latent_slot_invariance_pass = true`
- `latent_slot_max_abs_delta = 0`
- `slot_view_balance_pass = true`
- `coarse_slot_topk_preference_lookup_near_null_pass = true`
- `within_state_topk_preference_variation_pass = true`

## Intended Primary Metrics
- `accuracy`
- `f1`

## Scope Constraint
- memo-only until a dedicated approval gate exists
