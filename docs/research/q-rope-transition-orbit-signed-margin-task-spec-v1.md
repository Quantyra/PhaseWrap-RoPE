# Q-RoPE Transition Orbit Signed-Margin Task Specification v1

Date: 2026-03-11
Stories: S401

## Task ID
- `synthetic_transition_orbit_signed_margin_response`

## Objective
- predict the signed top-two latent margin inside each fixed four-candidate transition-orbit list
- positive target means the latent top candidate is separated in the forward direction
- negative target means the latent separation favors the opposite directional ordering

## Construction Rule
- reuse the same four-candidate within-state list shape as the stopped order-margin line
- compute latent candidate scores from the orbit-transition latent band quantity
- derive the target as:
  - `signed_margin = score_top1 - score_top2`
  - preserve sign rather than taking absolute value
- center signed-margin means across coarse transition states so coarse lookup should be near-null

## Why This Is Materially Different
- the stopped order-margin line used unsigned top-two gap magnitude
- this line makes directional separation primary
- it preserves the only unresolved signal from the stopped branch:
  - lower MAE with unstable ordering sign behavior

## Required Generator Diagnostics
- `coarse_signed_margin_lookup_near_null_pass`
- `within_state_signed_margin_variation_pass`
- `signed_margin_balance_pass`
- `token_view_balance_pass`

## Rejection Rule
- reject the task if coarse transition state alone predicts signed margin mean away from the centered global mean
- reject the task if within-state signed-margin variation collapses
