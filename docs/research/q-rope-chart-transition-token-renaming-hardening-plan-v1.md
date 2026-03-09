# Chart-transition token-renaming hardening plan

## Goal
Test whether the current witness advantage survives a fixed label-preserving token renaming on the same chart-transition task.

## Bounded next step
- rerun the witness and the strongest current symbolic baseline under `token_permutation=cdab`

## Constraint
- keep the same task
- keep the same seeds
- keep the same witness candidate
- use one fixed token permutation only
- do not add new symbolic families during this hardening step

## Decision rule
- if the witness remains stronger under the renamed-token packet, keep the branch active
- if the witness advantage collapses, the branch loses robustness value
