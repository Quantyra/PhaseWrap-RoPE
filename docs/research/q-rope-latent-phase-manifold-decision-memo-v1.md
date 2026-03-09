# Latent phase manifold decision memo

## Decision
- stop the current latent phase manifold branch
- return it to memo-only posture

## Why
The branch failed its first bounded packet. The witness did not beat every fixed control on mean MAE, which was the declared stop rule. In particular, the analog-only, nonlinear manifold, and global-phase symbolic controls all outperformed the witness on the primary regression metric.

## What is now disallowed
- no packet expansion on `synthetic_dual_latent_phase_manifold_residual_response`
- no additional controls on this task
- no remote execution
- no benchmark expansion

## Preserved next angle
- `local atlas manifold residual response`

## Rationale for the next angle
The current task still allowed a bounded global-phase control family to remain competitive. The next future task must require locally charted residual structure that cannot be captured by one global phase family or one fixed nonlinear basis over declared analog factors.
