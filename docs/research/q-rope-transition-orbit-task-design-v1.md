# Transition Orbit Task Design v1

## Intent
Preserve one memo-only next angle after the token-invariant branch failed.

## Direction
- Future task family: `synthetic_transition_orbit_response`
- Core requirement:
  - token identity must be collapsed into orbit-equivalence classes at task construction time
  - not merely checked afterward by paired render diagnostics
- Future controls must still include bounded transition-family symbolic regressors.

## Why this is materially different
- The failed branch still exposed token views to the learner through duplicated rendered examples, even though the latent target stayed invariant.
- The next angle removes token identity earlier, at the latent-task design layer.

## Status
- memo-only
- not approval-candidate
- no implementation authorized
