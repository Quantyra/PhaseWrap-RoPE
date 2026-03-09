# Transition cross-direction interaction control plan

## Goal
Test whether the current witness advantage is just a bounded interaction between forward and reversed transition-family responses rather than a stronger relational mechanism.

## Bounded next control
- `V_control_symbolic_transition_cross_direction_regressor`

## Constraint
- use the same declared analog factors
- keep ordered transition structure
- expose forward, reversed, and one bounded set of forward-reversed interaction terms only
- do not add chart-id one-hot features
- do not add uncontrolled higher-order basis expansion

## Decision rule
- if the cross-direction interaction control matches the witness on the primary metric, the current task is no longer a uniqueness test
- if the cross-direction interaction control remains weaker, keep the branch active
