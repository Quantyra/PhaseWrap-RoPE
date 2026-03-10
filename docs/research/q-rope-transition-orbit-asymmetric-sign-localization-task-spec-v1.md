# Q-RoPE Transition Orbit Asymmetric Sign-Localization Task Specification v1

Date: 2026-03-11
Stories: S437

## Task ID
- `synthetic_transition_orbit_asymmetric_sign_localization_binary`

## Objective
- predict which of two asymmetric paired-context perturbation channels localizes the latent sign change of the top-two transition-orbit margin
- positive label means the sign change localizes to channel `L`
- negative label means the sign change localizes to channel `R`

## Construction Rule
- start from the same orbit-canonical transition state family used by the stopped sign-flip contrast line
- build one anchor context plus two asymmetric perturbation contexts `L` and `R` per example
- hold the coarse transition state fixed across all three contexts
- require exactly one perturbation channel to flip the latent top-two sign while the other preserves it
- emit the binary label from which perturbation channel causes the flip
- center localization labels inside each coarse transition state so coarse localization lookup is near-null by construction
- keep token identity as a nuisance variable rather than a label carrier

## Required Generator Diagnostics
- `coarse_localization_lookup_near_null_pass`
- `within_state_localization_variation_pass`
- `paired_channel_diversity_pass`
- `localization_label_balance_pass`
- `token_view_balance_pass`

## Why This Is Materially Different
- the stopped sign-flip contrast line only asked whether a flip occurred
- this line asks where the directional change localizes across asymmetric perturbation channels
- it forces the next branch to represent asymmetric contextual directionality, not just binary flip-versus-hold structure

## Rejection Rule
- reject the task if coarse transition state alone predicts localization imbalance away from the centered global rate
- reject the task if both perturbation channels become effectively interchangeable
- reject the task if within-state localization variation collapses
