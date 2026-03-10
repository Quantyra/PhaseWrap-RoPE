# Q-RoPE Transition Orbit Sign-Consistency Task Specification v1

Date: 2026-03-11
Stories: S419

## Task ID
- `synthetic_transition_orbit_sign_consistency_binary`

## Objective
- predict whether the latent sign of the top-two transition-orbit margin is preserved across two related within-state list contexts
- positive label means the directional sign agrees across the paired contexts
- negative label means the directional sign flips across the paired contexts

## Construction Rule
- start from the same orbit-canonical transition state family used by the sign-only line
- for each retained coarse transition state, construct paired list contexts `A` and `B` that preserve the same coarse state but change the within-state pairing realization
- derive one latent signed top-two margin per context
- emit a binary consistency label from `sign(margin_A) == sign(margin_B)` only
- enforce class balance inside each coarse transition state so coarse consistency lookup should be near-null by construction
- keep token identity as a nuisance variable rather than a label carrier

## Required Generator Diagnostics
- `coarse_consistency_lookup_near_null_pass`
- `within_state_consistency_variation_pass`
- `paired_context_diversity_pass`
- `consistency_label_balance_pass`
- `token_view_balance_pass`

## Why This Is Materially Different
- the stopped sign-only branch supervised a single-context directional label
- this line supervises directional stability across paired contexts
- it tests whether the witness preserves relational sign structure under controlled context perturbation rather than simply predicting one local sign

## Rejection Rule
- reject the task if coarse transition state alone predicts consistency imbalance away from the centered global rate
- reject the task if paired contexts collapse to one effective view
- reject the task if within-state consistency variation collapses
