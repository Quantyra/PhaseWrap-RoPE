# Transition-family permutation control plan

## Goal
Test whether the current witness advantage depends on one favorable ordered transition family table or whether it survives a deterministic permutation of the ordered transition family assignments.

## Bounded next control
- `V_control_symbolic_transition_permuted_regressor`

## Constraint
- use the same declared analog factors
- keep ordered source-destination structure
- deterministically permute the transition family assignment table
- do not add chart-id one-hot features
- do not add new nonlinear basis expansion

## Decision rule
- if the permuted transition control matches the witness on the primary metric, the current task is no longer a uniqueness test
- if the permuted transition control remains weaker, keep the branch active
