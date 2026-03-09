# Local atlas manifold decision memo

## Decision
- stop the current local atlas manifold branch
- return it to memo-only posture

## Why
The branch failed its first bounded packet. The witness did not beat every fixed control on mean MAE, which was the declared stop rule. In particular, the nonlinear manifold, phase-insensitive, and bounded single-chart symbolic controls all outperformed the witness on the primary regression metric.

## What is now disallowed
- no packet expansion on `synthetic_dual_local_atlas_manifold_response`
- no additional controls on this task
- no remote execution
- no benchmark expansion

## Preserved next angle
- `chart-transition manifold residual response`

## Rationale for the next angle
The current task still allowed a bounded single-chart control to remain competitive. The next future task must require transition-sensitive structure between local charts rather than chart-local residuals alone.
