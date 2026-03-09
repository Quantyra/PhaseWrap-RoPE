# Phase-sensitive manifold task design

## Motivation
The current nonlinear manifold task defeated additive controls but not a direct symbolic nonlinear control built from the declared target geometry. The next task must require structure that is not recoverable from a small fixed nonlinear regressor over the same declared analog factors.

## Preserved next angle
- future task family: `phase-sensitive manifold residual response`

## Requirement
A future target should depend on relational analog structure in a way that cannot be captured by one fixed symbolic transform family derived directly from the task memo, for example:
- phase-wrapped residual structure with local ambiguity under low-order transforms
- manifold response requiring sector-conditioned curvature shifts rather than one global nonlinear basis
- piecewise-smooth analog target with controlled discontinuity placement that defeats a fixed symbolic manifold regressor

## Future restart bar
Do not approve a future implementation unless the task memo proves all of the following:
- coarse lookup is near-null
- additive analog controls are insufficient
- the currently successful direct nonlinear control family is intentionally insufficient by construction
