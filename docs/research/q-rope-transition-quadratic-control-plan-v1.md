# Quadratic transition-family control plan

## Goal
Test whether the current witness advantage is just a small fixed quadratic expansion of the declared transition-family features rather than a stronger relational mechanism.

## Bounded next control
- `V_control_symbolic_transition_quadratic_regressor`

## Constraint
- use the same declared analog factors
- keep ordered transition structure
- expose the declared transition-family features plus one fixed bounded quadratic basis only
- do not add chart-id one-hot features
- do not add uncontrolled higher-order basis expansion beyond the fixed quadratic set

## Decision rule
- if the quadratic control matches the witness on the primary metric, the current task is no longer a uniqueness test
- if the quadratic control remains weaker, keep the branch active
