# Q-RoPE Representation-Angle Memo v1

## Status
- `memo-only`
- `archive-safe`
- `not approved for implementation`

## Core idea
The next viable angle may be to stop treating relative position as phase that must be recovered through the same downstream score/readout path, and instead represent relative position as an explicit relational quantum object before measurement.

That is materially different from the failed lines in this repo.

## Why this angle exists
The repeated failure pattern was:
- phase existed,
- but the scoring/comparison/observable path did not convert it into stronger relative-offset discrimination.

The likely lesson is not just "bad comparator tuning."
It may be that the representation target itself was wrong.

## Proposed angle
Instead of encoding position only as branch-local phase and hoping a later observable recovers the relation, encode the relation directly in one of these forms:

1. `pair-state representation`
- Build a joint token-pair state `(x_i, x_j, i, j)` and encode relative offset as a structured subspace relation, not just independent phase tags on two states.

2. `difference-register representation`
- Map `j - i` into a constrained relative-position register or register-like subspace that is interrogated directly by the observable.

3. `relational interference scaffold`
- Force constructive/destructive behavior around relative-offset classes first, and only then mix in content, rather than treating content and position as parallel factors from the start.

## Why this differs from what already failed
This is not:
- `V4`
- `V4b`
- local readout tuning
- local tail tuning
- pairwise-overlap similarity
- parity-contrast on the same branch-local representation

Those lines all assumed the relative signal should emerge from roughly the same content-plus-phase state geometry.

This memo questions that assumption directly.

## Strongest candidate under this angle
The strongest memo-level candidate is:
- `pair-state relative-offset encoding`

Reason:
- it is the cleanest way to make the relation itself explicit
- it gives a future observable something relational to read
- it avoids relying on later stages to infer `j - i` indirectly from two loosely coupled branch states

## What a future restart would have to prove
A future restart under this angle would need to show:
1. the representation explicitly separates relative-offset classes
2. the observable reads that separation directly
3. synthetic offset diagnostics improve because of relational structure, not because of a uniform score shift

## What not to do
Do not translate this memo into code by inertia.

Before any restart brief, Quantyra would still need:
- exact representation design
- exact observable
- exact synthetic falsification packet
- explicit proof that it is not just another rephrasing of the failed local comparator line

## Bottom line
Yes, there is a different angle worth preserving.

The most credible one is:
- stop asking the measurement stack to recover relative position from branch-local phase alone
- start representing relative position as an explicit relational quantum object

That is the right memo-level direction if Quantyra wants a future restart that is meaningfully different from the branches already closed.

