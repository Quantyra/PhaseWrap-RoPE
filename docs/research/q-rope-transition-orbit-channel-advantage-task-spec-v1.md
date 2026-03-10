# Q-RoPE Transition Orbit Channel-Advantage Task Specification v1

Date: 2026-03-10
Stories: S446

## Task ID
- `synthetic_transition_orbit_channel_advantage_response`

## Objective
- predict the signed advantage of perturbation channel `L` over perturbation channel `R` with respect to the latent top-two transition-orbit margin
- positive target means the `L` perturbation induces the stronger directional effect
- negative target means the `R` perturbation induces the stronger directional effect

## Construction Rule
- start from the same orbit-canonical transition state family used by the stopped asymmetric localization line
- build one anchor context plus two asymmetric perturbation contexts `L` and `R` per example
- hold the coarse transition state fixed across all three contexts
- compute one latent signed channel effect per perturbation relative to the shared anchor
- emit the regression target from the centered signed difference:
  - `effect_L - effect_R`
- center the target within each coarse transition state so coarse lookup is near-null by construction
- keep token identity as a nuisance variable rather than a target carrier

## Required Generator Diagnostics
- `coarse_channel_advantage_lookup_near_null_pass`
- `within_state_channel_advantage_variation_pass`
- `paired_channel_diversity_pass`
- `channel_advantage_balance_pass`
- `token_view_balance_pass`

## Why This Is Materially Different
- the stopped asymmetric localization line asked for binary channel identity
- this line supervises signed relative channel effect magnitude
- it preserves directional asymmetry while avoiding the zero-positive-class collapse of the binary formulation

## Rejection Rule
- reject the task if coarse transition state alone predicts target mean away from the centered global mean
- reject the task if both perturbation channels become effectively interchangeable
- reject the task if within-state channel-advantage variation collapses
