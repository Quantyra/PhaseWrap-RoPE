# Unordered transition control plan

## Goal
Test whether the current witness advantage depends on ordered transition structure or whether the same signal survives under an unordered transition symbolic control.

## Bounded next control
- `V_control_symbolic_transition_unordered_regressor`

## Constraint
- use the same declared analog factors and the same bounded transition family
- collapse `(source, dest)` and `(dest, source)` into the same symbolic response family
- do not add chart-id one-hot features
- do not add new global nonlinear basis expansion

## Decision rule
- if unordered transition control matches the witness on the primary metric, the current task is no longer a uniqueness test
- if unordered transition control remains meaningfully weaker, keep the branch active
