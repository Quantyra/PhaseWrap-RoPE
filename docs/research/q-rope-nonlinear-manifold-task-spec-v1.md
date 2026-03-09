# Nonlinear manifold task specification

## Task
- `synthetic_dual_nonlinear_manifold_response`

## Motivation
The orthogonalized continuous branch removed the coarse lookup shortcut, but simple additive analog regressors still explained the target too well. The next task must keep coarse lookup near-null and make additive analog baselines intentionally insufficient by construction.

## Structure
Each sample contains two ordered observations derived from the existing dual relational generator. The target is computed from declared analog factors but mapped through a nonlinear manifold response rather than an additive rule.

## Declared analog factors
- `sector_magnitude_delta`
- `ordered_content_delta`
- `orientation_delta`

## Target rule
Let:
- `u = sector_magnitude_delta`
- `v = ordered_content_delta`
- `w = orientation_delta`

Define the raw response as:
- `r = sin(pi * u * v) + 0.5 * sign(u) * w - 0.25 * cos(pi * v)`

Then center the response within each coarse agreement tuple so coarse lookup remains near-null.

## Required properties
- Coarse agreement tuple means must be near zero after centering.
- Additive regressors over `u`, `v`, `w` alone should be intentionally misspecified.
- The target must retain within-state variation after centering.

## Rejection rule
Reject the task if either of the following is true:
- coarse lookup remains materially predictive after centering
- a declared additive analog regressor is sufficient without nonlinear interaction terms
