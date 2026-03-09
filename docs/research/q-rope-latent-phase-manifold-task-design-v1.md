# Latent phase manifold task design

## Motivation
The phase-sensitive manifold task failed because bounded symbolic nonlinear controls still explained the target more effectively than the witness path. A future task must require structure that is not recoverable from directly declared analog factors plus a fixed phase-insensitive or phase-conditioned transform family.

## Preserved next angle
- future task family: `latent phase manifold residual response`

## Requirement
A future target should depend on relational structure through a latent phase assignment that is not directly exposed as a simple closed-form transform of the declared analog factors, while still preserving auditable bounds. Examples:
- hidden phase family selected by a constrained latent partition over relational states
- residual target that depends on phase-wrapped local neighborhoods rather than one global phase offset map
- manifold response with controlled local aliasing that defeats both direct nonlinear basis features and simple phase-insensitive approximations

## Future restart bar
Do not approve a future implementation unless the task memo proves all of the following:
- coarse lookup is near-null
- additive analog controls are insufficient
- the current nonlinear and phase-insensitive symbolic control families are intentionally insufficient by construction
