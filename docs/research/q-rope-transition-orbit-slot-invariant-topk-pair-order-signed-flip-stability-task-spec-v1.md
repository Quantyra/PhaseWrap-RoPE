# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Flip Stability Task Specification v1

Date: 2026-03-11
Stories: S599

## Task ID
- `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary`

## Objective
- predict whether the latent signed top-k pair-order flip relation remains stable across paired slot-invariant contexts under bounded within-state perturbation
- positive label means the paired contexts preserve the same signed-flip disposition under the approved perturbation family
- negative label means the signed-flip disposition changes across the paired contexts

## Construction Rule
- start from the same slot-invariant latent state family used by the stopped signed-flip consistency line
- preserve latent slot invariance by construction under paired rendered views
- for each retained coarse slot-invariant state, construct two paired contexts `A` and `B` with nontrivial within-state pair-order variation
- derive one latent signed top-k pair-order flip indicator per paired context
- emit a binary stability label from `flip_indicator_A == flip_indicator_B` only
- enforce class balance inside each coarse slot state so coarse signed-flip stability lookup should be near-null by construction
- keep token identity and slot identity as nuisance variables rather than label carriers

## Required Generator Diagnostics
- `latent_slot_invariance_pass`
- `latent_slot_max_abs_delta = 0`
- `slot_view_balance_pass`
- `coarse_slot_topk_pair_signed_flip_stability_lookup_near_null_pass`
- `within_state_topk_pair_signed_flip_stability_variation_pass`
- `paired_context_diversity_pass`
- `signed_flip_stability_label_balance_pass`

## Rejection Rule
- reject the task if coarse slot state alone predicts stability imbalance away from the centered global rate
- reject the task if paired contexts collapse to one effective view
- reject the task if within-state signed-flip stability variation collapses
