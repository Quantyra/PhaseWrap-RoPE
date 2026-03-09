# Cubic transition-family control plan

## Goal
Test whether the current witness advantage is just a small fixed cubic expansion of the declared transition-family features rather than a stronger relational mechanism.

## Bounded next control
- `V_control_symbolic_transition_cubic_regressor`

## Constraint
- use the same declared analog factors
- keep ordered transition structure
- expose the declared transition-family features plus one fixed bounded cubic basis only
- do not add chart-id one-hot features
- do not add uncontrolled higher-order basis expansion beyond the fixed cubic set

## Decision rule
- if the cubic control matches the witness on the primary metric, the current task is no longer a uniqueness test
- if the cubic control remains weaker, keep the branch active
