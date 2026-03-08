# Q-RoPE Pair-State Construction Memo v1

## Status
- `memo-only`
- `archive-safe`
- `not approved for implementation`

## Goal
Provide one operational construction sketch for `V_pairstate_relational` that is concrete enough to evaluate at memo level.

## Candidate construction sketch
Use a three-block construction:

1. `content block`
- encode the ordered token pair `(x_i, x_j)` into a joint content pattern
- this block should distinguish:
  - same-token pairs
  - cross-token pairs
  - order-sensitive token identity

2. `offset-sector block`
- encode signed offset sector membership:
  - `P_small`, `P_large`, `N_small`, `N_large`
- this block should be explicit and directly recoverable at the measurement layer

3. `coupling block`
- apply a controlled mixing rule so that content structure modulates sector response
- goal:
  - not to reconstruct offset from content
  - but to test whether content and offset are jointly represented in a coherent relational pattern

## Minimal operational intuition
The pair-state should look conceptually like:
- `|psi_pair> = Coupling( Content(x_i, x_j), Sector(j-i) )`

where:
- `Content(x_i, x_j)` is not itself the answer
- `Sector(j-i)` is not itself the answer
- the useful signal is in how the observable reads their coupled structure

## Why this is different from the failed line
The failed line relied on:
- independent content-bearing branches
- independent position-bearing phase
- a later score/readout trying to infer relation from the combined aftermath

This construction says:
- make the relation explicit first
- couple it to content second
- read relational sectors directly third

That ordering is the substantive difference.

## What would count as a bad construction
This candidate should be rejected if, on closer inspection, it reduces to:
- a disguised global scalar score
- another branch-local overlap in different notation
- content dominating sectors so strongly that sector responses become decorative only

## What would count as a promising construction
Promising qualities would be:
- sector membership remains interpretable
- content changes modulate but do not erase sector contrast
- positive/negative separation can be inspected before total aggregation

## Remaining gap after this memo
The pair-state direction still lacks:
- an exact measurement operator
- an exact low-level encoding rule for the content block

So this memo sharpens the operational picture but does not finish the design.

## Bottom line
The pair-state direction is now operationally more coherent on paper:
- content block
- sector block
- coupling block

That is enough to continue memo-level evaluation without pretending the design is implementation-ready.

