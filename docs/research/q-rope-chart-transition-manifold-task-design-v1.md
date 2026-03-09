# Chart-transition manifold task design

## Motivation
The local atlas manifold branch failed because a bounded single-chart symbolic control and the current nonlinear and phase-insensitive families remained sufficient on the primary metric. A future task must require structure that depends on transitions between local charts rather than one chart-local residual family.

## Preserved next angle
- future task family: `chart-transition manifold residual response`

## Requirement
A future target should:
- preserve near-null coarse lookup by construction
- defeat additive analog controls by construction
- defeat the current nonlinear manifold family by construction
- defeat the current phase-insensitive and bounded global-phase families by construction
- defeat one bounded single-chart symbolic control by construction
- require transition-sensitive residual routing across neighboring charts rather than one chart-local response alone

## Future restart bar
Do not approve a future implementation unless the task memo proves all of the following:
- coarse lookup is near-null
- additive analog controls are insufficient
- the current nonlinear, phase-insensitive, and bounded global-phase families are insufficient
- a bounded single-chart symbolic control is insufficient
- the transition-sensitive residual cannot be rewritten as one chart-local or one global transform over declared analog factors
