# Q-RoPE Pair-State Restart Brief Scaffold v1

## Status
- `memo-only`
- `archive-safe`
- `not approved for implementation`

## Candidate name
- `V_pairstate_relational`

## Mechanism summary
This candidate treats the token pair as the primitive object and encodes relative offset as explicit state structure rather than expecting two branch-local states to reveal the relation later.

## Representation
- prepare one joint pair-state over `(x_i, x_j, i, j)`
- allocate explicit relative-offset sectors inside the prepared state
- couple token-pair content with relative-offset structure so the relation is first-class

## Observable
- use sector-contrast relational measurement
- target quantity:
  - positive-sector response minus negative-sector response
- optional refinement:
  - contrast broken down by offset magnitude classes

## Why this is materially different
It does not rely on:
- branch-local phase tags
- later overlap recovery
- one global scalar readout over an implicitly relational state

It changes both:
- the represented object
- the measured object

## Minimal future restart brief requirements
A future restart brief based on this scaffold must still specify:
1. exact pair-state preparation rule
2. exact sector definition
3. exact measurement operator or rule
4. exact aggregation rule
5. exact synthetic run configuration

## Fixed first falsification packet
- dataset: `synthetic_offset_binary`
- seeds: `42`, `123`, `777`
- baseline: `V0`
- candidate: `V_pairstate_relational`
- scope: local-only
- remote work: forbidden

## Pass condition
Only pass if all are true:
1. signed offset separation improves over `V0`
2. the direction holds across all three seeds
3. sector-level diagnostics confirm real relational contrast
4. gains are not explainable as a uniform score shift

## Fail condition
Fail immediately if:
1. offset separation is mixed or absent
2. the result is one-seed dependent
3. the signal is only a global score shift
4. sector contrast does not distinguish positive vs negative offsets

## What this scaffold is for
This is not a restart brief.
It is the smallest coherent package that a future restart brief can build on.

## Bottom line
If Quantyra wants the cleanest preserved next direction, this is it:
- pair-state representation
- sector-contrast observable
- fixed synthetic gate

That is enough to support future memo-level restart work without reopening implementation today.

