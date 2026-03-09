# State-sensitive continuous task specification

## Task
- `synthetic_dual_state_sensitive_continuous_response`

## Purpose
Preserve one harder continuous relational target whose response varies inside the same coarse boolean agreement state, so a bounded lookup over `(sign_agreement, content_agreement, orientation_agreement)` is structurally insufficient.

## Variables
Each dual observation pair still exposes the same three coarse relational families:
- `sign_agreement`
- `content_agreement`
- `orientation_agreement`

The new task adds two within-state analog factors:
- `sector_magnitude_delta`
  - normalized difference between the absolute offsets in observation `a` and observation `b`
- `ordered_content_delta`
  - graded ordered-token composition score that distinguishes ordered token-pair structure inside the same coarse content family

## Target rule
For a future implementation, the target must be a real-valued function of the form:
- `target = coarse_term + state_sensitive_term`

Where:
- `coarse_term` is a bounded linear combination of the three agreement families
- `state_sensitive_term` is a bounded combination of `sector_magnitude_delta` and `ordered_content_delta`
- `state_sensitive_term` must vary across samples that share the same `(sign_agreement, content_agreement, orientation_agreement)` tuple

## Anti-shortcut rule
Reject the task if either of these becomes true:
- all targets are determined by the three coarse agreement bits alone
- the within-state analog factors collapse to a constant inside each coarse agreement tuple

## Intended control consequence
A future bounded symbolic lookup over the three coarse agreement bits should be insufficient by construction.
A fair future control stack would need to declare whether it is allowed to see the new analog factors directly.
