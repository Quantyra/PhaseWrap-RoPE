# Local atlas manifold task specification

## Task
- `synthetic_dual_local_atlas_manifold_response`

## Motivation
The latent phase manifold branch failed because a bounded global-phase symbolic control and the current nonlinear manifold family still explained the target too well. The next task must require multiple local charts with chart-specific residual structure so one global residual map is intentionally insufficient.

## Declared analog factors
- `sector_magnitude_delta`
- `ordered_content_delta`
- `orientation_delta`

## Local atlas structure
Define a bounded atlas over relational analog space with multiple local charts. Each sample belongs to one chart according to a deterministic but unexposed chart-assignment rule. The target must combine:
- one shared analog backbone over declared factors
- one chart-local residual family
- one bounded transition rule between neighboring charts

## Required properties
- coarse agreement tuple means must be near zero after centering
- additive analog controls must be intentionally insufficient
- the current nonlinear manifold family must be intentionally insufficient
- the current phase-insensitive family must be intentionally insufficient
- the current bounded global-phase family must be intentionally insufficient
- one chart-local residual must not be recoverable as a single global transform over declared analog factors

## Rejection rule
Reject the task if any of the following is true:
- coarse lookup remains materially predictive after centering
- one global nonlinear symbolic family is sufficient
- one bounded global-phase family is sufficient
- chart transitions collapse into a direct closed-form transform of declared analog factors
