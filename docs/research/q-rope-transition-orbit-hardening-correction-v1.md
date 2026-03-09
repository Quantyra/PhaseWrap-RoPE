# Transition Orbit Hardening Correction Memo v1

## Correction
- withdraw latent chart-id relabeling as the next execution step for `synthetic_chart_transition_orbit_response`

## Why
- the current task target is chart-table defined
- a chart-id relabel would change the task semantics rather than provide a label-preserving perturbation
- that makes chart relabeling a new task design question, not a hardening step

## Replacement hardening
- use `pair_reindex = 7`
- keep labels, orbit structure, and control stack fixed
