# Q-RoPE Pair-State Representation Memo v1

## Status
- `memo-only`
- `archive-safe`
- `not approved for implementation`

## Candidate family
Use a `pair-state relative-offset representation` instead of two independent branch-local states.

Target form:
- prepare one joint state over `(x_i, x_j, i, j)`
- encode the relative relation inside the state construction itself
- measure a relational observable on the joint state rather than comparing two separately prepared states after the fact

## Why this is different
The stopped branches assumed:
- content was loaded separately
- position was loaded separately
- a later score/readout path would recover the useful relative structure

This candidate changes that assumption.

The relation is no longer inferred from:
- `P(i) E(x_i)` versus `P(j) E(x_j)`

Instead, the pair is the primitive object.

## One concrete memo-level version
Use a joint token-pair basis with a relative-offset-coded subspace:

1. content block
- load token-pair content `(x_i, x_j)` into a joint amplitude or angle pattern

2. relative-offset block
- encode `j - i` directly into a constrained set of basis sectors or phase-labeled sectors

3. coupling block
- couple content sectors and relative-offset sectors so the observable can test whether content and offset cohere, rather than reading either one alone

## Why this may help
This candidate may help because it removes one repeated failure mode:
- the observable no longer has to reconstruct the relation from two loosely coupled branch-local states

Instead, the relation is present as a first-class part of the prepared state.

## What a future observable should test
A future observable under this family should ask:
- does the joint state distinguish positive versus negative offsets directly?
- does that distinction survive content variation?
- does the signal come from the relative-offset block rather than a uniform score shift?

## What would make this falsifiable
Before any restart brief, this family would still need:
1. exact pair-state preparation rule
2. exact relative-offset sector definition
3. exact relational observable
4. exact synthetic falsification packet

## What this is not
This is not:
- another parity tweak on the old local simulator path
- another overlap score
- another interference contrast over the same branch-local representation

## Bottom line
If Quantyra wants one concrete new representation-level family worth preserving, this is the leading candidate:
- `pair-state relative-offset encoding`

It is specific enough to guide future memo work and still different enough from the failed branches to justify being kept alive at the design level.

