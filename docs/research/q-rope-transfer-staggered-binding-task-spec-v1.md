# Q-RoPE Transfer Staggered Binding Task Spec v1

Date: 2026-03-13
Stories: S1014

## Task
- `synthetic_symbolic_insufficiency_staggered_binding_response`

## Objective
Test whether the witness advantage survives on a delayed multi-stage binding task where value is carried through an intermediate staging phase before final binding resolves the response.

## Structural Form
- `source -> stage_a -> stage_b -> bind`
- The target depends on:
  - staged persistence across `stage_a` and `stage_b`
  - final bind resolution
  - latent-conditioned interaction between early staging and late binding

## Required Generator Diagnostics
- `coarse_staggered_state_null_pass`
- `within_staggered_state_variation_pass`
- `latent_staggered_diversity_pass`
- `token_view_balance_pass`
- `staged_binding_target_nontrivial_pass`

## Exclusion Rule
Reject the family if the target can be reduced to a compact summary of the final bind alone.
