# Transition-bidirectional control plan

## Goal
Test whether the current witness advantage depends on separating forward and reversed ordered transition families only because the control stack has seen them one at a time.

## Bounded next control
- `V_control_symbolic_transition_bidirectional_regressor`

## Constraint
- use the same declared analog factors
- keep ordered transition structure
- expose both forward and reversed transition-family responses in one bounded linear control
- do not add chart-id one-hot features
- do not add uncontrolled nonlinear basis expansion

## Decision rule
- if the bidirectional control matches the witness on the primary metric, the current task is no longer a uniqueness test
- if the bidirectional control remains weaker, keep the branch active
