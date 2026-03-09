# Phase-sensitive manifold task specification

## Task
- `synthetic_dual_phase_sensitive_manifold_response`

## Motivation
The current nonlinear manifold task is exhausted because one fixed symbolic nonlinear control family over declared analog factors is already sufficient. The next task must require residual structure that changes with relational state in a way a single global nonlinear basis should not capture cleanly.

## Declared analog factors
- `sector_magnitude_delta`
- `ordered_content_delta`
- `orientation_delta`

## State-conditioned phase families
Define the coarse relational state by:
- `sign_agreement`
- `content_agreement`
- `orientation_agreement`

Map that state to a bounded phase offset family rather than a direct label lookup.

## Target rule
Let:
- `u = sector_magnitude_delta`
- `v = ordered_content_delta`
- `w = orientation_delta`
- `phi(state)` be one of four bounded phase offsets assigned by the agreement tuple family

Define the raw response as:
- `r = sin(pi * u * v + phi(state)) + 0.35 * cos(pi * (v + w))`

Then center the response within each coarse agreement tuple so coarse lookup remains near-null.

## Required properties
- coarse tuple means must be near zero after centering
- within-state variation must remain nontrivial after centering
- one fixed global nonlinear feature family over `u`, `v`, `w` should be intentionally insufficient

## Rejection rule
Reject the task if any of the following is true:
- coarse lookup remains materially predictive after centering
- an additive analog regressor remains sufficient
- the current direct nonlinear manifold control family remains sufficient without state-conditioned phase structure
