# Chart-transition post-cubic decision

## Decision
- keep the chart-transition manifold branch active
- stop escalating bounded symbolic basis size on this task
- switch the next bounded step to a hardening test

## Why
The witness remained stronger than the cubic control on both the primary metric and rank correlation. The cubic basis did not improve over the quadratic basis in any meaningful way, so continued symbolic basis expansion is now a weak use of branch budget.

## Next bounded question
- does the chart-transition witness survive a fixed token-renaming hardening on the same task?

## Why this is the right next control
The branch has now survived linear, directional, cross-direction, quadratic, and cubic symbolic families. The next useful information is robustness under a label-preserving generator perturbation, not another broader symbolic regressor.
