# Transition-reversal control plan

## Goal
Test whether the current witness advantage depends on one directional convention or whether it survives a bounded control that reverses the ordered transition rule.

## Bounded next control
- `V_control_symbolic_transition_reversed_regressor`

## Constraint
- use the same declared analog factors
- keep ordered transition structure
- reverse the transition mapping direction inside the bounded symbolic family
- do not add chart-id one-hot features
- do not add new nonlinear basis expansion

## Decision rule
- if the reversed transition control matches the witness on the primary metric, the current task is no longer a uniqueness test
- if the reversed transition control remains weaker, keep the branch active
