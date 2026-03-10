# Q-RoPE Transition Orbit Sign-Flip Contrast Task Specification v1

Date: 2026-03-11
Stories: S428

## Task ID
- `synthetic_transition_orbit_sign_flip_contrast_binary`

## Objective
- predict whether a controlled paired-context perturbation flips the latent sign of the top-two transition-orbit margin
- positive label means `sign(margin_anchor) != sign(margin_perturbed)`
- negative label means `sign(margin_anchor) == sign(margin_perturbed)`

## Construction Rule
- start from the same orbit-canonical transition state family used by the stopped sign-consistency line
- build one anchor list context and one paired perturbed context per example
- hold the coarse transition state fixed
- require the perturbation to change within-state realization rather than token identity alone
- center flip/hold balance inside each coarse transition state so coarse flip lookup should be near-null by construction
- keep token identity as a nuisance variable rather than a label carrier

## Required Generator Diagnostics
- `coarse_flip_lookup_near_null_pass`
- `within_state_flip_variation_pass`
- `paired_context_diversity_pass`
- `flip_label_balance_pass`
- `token_view_balance_pass`

## Why This Is Materially Different
- the stopped sign-consistency branch supervised passive agreement across two contexts
- this line supervises active directional flip versus hold under a controlled perturbation
- it directly attacks the failure mode from the stopped branch:
  - weak consistency labels that still collapsed into zero positive-class F1

## Rejection Rule
- reject the task if coarse transition state alone predicts flip imbalance away from the centered global rate
- reject the task if paired contexts collapse to one effective view
- reject the task if within-state flip variation collapses
