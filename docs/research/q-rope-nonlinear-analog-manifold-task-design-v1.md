# Nonlinear analog manifold task design

## Motivation
The orthogonalized branch removed the coarse lookup shortcut, but the task still remained solvable by simple analog symbolic controls.

## Preserved next angle
- future task family: `nonlinear analog manifold relational response`

## Requirement
A future target should depend on analog structure in a way that cannot be captured by a small additive regressor over declared analog factors, for example:
- non-separable curved response over analog factors
- locally monotone but globally folded target geometry
- piecewise-coupled analog response with declared smoothness constraints

## Future restart bar
Do not approve a future implementation unless the task memo proves both:
- coarse lookup is near-null
- the declared additive analog baseline is intentionally insufficient by construction
