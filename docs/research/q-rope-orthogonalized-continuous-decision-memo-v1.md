# Orthogonalized continuous decision memo

## Decision
- `STOP` the implemented `synthetic_dual_orthogonalized_continuous_response` branch.
- Return the branch to memo-only posture.

## Basis
- The branch achieved its narrow fairness goal against the coarse lookup baseline.
- But the candidate still lost to both stronger symbolic controls:
  - analog-only regressor
  - full declared residual regressor

## Interpretation
- Coarse-state shortcut suppression was necessary, but not sufficient.
- The remaining task is still explainable by declared analog structure available to a bounded symbolic regressor.
- This branch does not justify expansion, tuning, or remote work.

## Preserved lesson
A future continuous task must force structure that is not recoverable from simple additive analog features alone.
