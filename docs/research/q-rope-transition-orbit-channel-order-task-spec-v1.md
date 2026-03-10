# Q-RoPE Transition Orbit Channel-Order Task Specification v1

Date: 2026-03-10
Stories: S455

## Task ID
- `synthetic_transition_orbit_channel_order_response`

## Objective
- predict the relative ordering between perturbation channel `L` and perturbation channel `R` with respect to the latent transition-orbit response
- positive target means channel `L` ranks above channel `R`
- negative target means channel `R` ranks above channel `L`
- zero target is disallowed in the retained packet

## Construction Rule
- start from the same anchor-plus-two-channel construction used by the stopped channel-advantage line
- hold the coarse transition state fixed across the anchor, `L`, and `R` contexts
- compute one latent channel response for `L` and one latent channel response for `R`
- discard raw signed effect magnitude and keep only the induced strict order between channels
- center retained examples so coarse transition state alone is near-null for the order target
- keep token identity as a nuisance variable rather than a target carrier

## Required Generator Diagnostics
- `coarse_channel_order_lookup_near_null_pass`
- `within_state_channel_order_variation_pass`
- `paired_channel_diversity_pass`
- `channel_order_balance_pass`
- `token_view_balance_pass`

## Why This Is Materially Different
- the stopped channel-advantage branch supervised raw signed effect difference and failed catastrophically through numerical instability
- this line strips away magnitude and tests only comparative ordering between the two channels
- it is the smallest coherent continuation of that branch rather than another direct magnitude regression

## Rejection Rule
- reject the task if coarse transition state alone predicts channel order away from the centered global rate
- reject the task if within-state channel-order variation collapses
- reject the task if the two perturbation channels become effectively interchangeable in the retained packet
