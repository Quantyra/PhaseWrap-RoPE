# Chart-transition manifold task specification

## Task
- `synthetic_dual_chart_transition_manifold_response`

## Motivation
The local atlas manifold branch failed because a bounded single-chart symbolic control remained sufficient on the primary metric. The next task must require response structure that depends on transitions between neighboring charts rather than any single chart-local residual family.

## Declared analog factors
- `sector_magnitude_delta`
- `ordered_content_delta`
- `orientation_delta`

## Transition structure
Define a bounded chart atlas over relational analog space and a deterministic but unexposed transition operator between neighboring charts. Each sample must carry:
- one source chart assignment
- one destination chart assignment
- one transition-sensitive residual term that depends on the ordered chart pair rather than either chart alone

## Required properties
- coarse agreement tuple means must be near zero after centering
- additive analog controls must be intentionally insufficient
- the current nonlinear manifold family must be intentionally insufficient
- the current phase-insensitive and bounded global-phase families must be intentionally insufficient
- a bounded single-chart symbolic control must be intentionally insufficient
- the target must not collapse into one chart-local or one global residual map over declared analog factors

## Rejection rule
Reject the task if any of the following is true:
- coarse lookup remains materially predictive after centering
- one global nonlinear symbolic family is sufficient
- one bounded global-phase family is sufficient
- one bounded single-chart symbolic family is sufficient
- the transition-sensitive residual can be rewritten as one chart-local or one global transform over declared analog factors
