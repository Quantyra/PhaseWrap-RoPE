# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Flip Persistence Task Specification v1

Date: 2026-03-11
Stories: S608

## Task ID
- `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary`

## Objective
- predict whether the latent signed top-k pair-order flip pattern persists across an extended paired-context chain under slot-invariant nuisance rendering
- positive label means the same signed-flip disposition persists across the retained paired contexts
- negative label means persistence breaks across the paired contexts

## Construction Rule
- start from the same slot-invariant latent state family used by the stopped signed-flip stability line
- preserve latent slot invariance by construction under paired rendered views
- for each retained coarse slot-invariant state, construct an extended paired-context chain with nontrivial within-state pair-order variation
- derive one latent signed top-k pair-order flip indicator per retained context in the chain
- emit a binary persistence label from whether that signed-flip disposition remains unchanged across the full retained chain
- enforce class balance inside each coarse slot state so coarse signed-flip persistence lookup should be near-null by construction
- keep token identity and slot identity as nuisance variables rather than label carriers

## Required Generator Diagnostics
- `latent_slot_invariance_pass`
- `latent_slot_max_abs_delta = 0`
- `slot_view_balance_pass`
- `coarse_slot_topk_pair_signed_flip_persistence_lookup_near_null_pass`
- `within_state_topk_pair_signed_flip_persistence_variation_pass`
- `paired_context_diversity_pass`
- `signed_flip_persistence_label_balance_pass`

## Rejection Rule
- reject the task if coarse slot state alone predicts persistence imbalance away from the centered global rate
- reject the task if the paired-context chain collapses to one effective comparison
- reject the task if within-state signed-flip persistence variation collapses
