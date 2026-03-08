# Q-RoPE Pair-State Measurement Realization Memo v1

## Status
- `memo-only`
- `archive-safe`
- `not approved for implementation`

## Goal
Close the remaining measurement-realization gap for `V_pairstate_relational` at the memo level.

## Candidate realization rule
Use a `sector-first measurement pipeline`:

1. resolve sector membership first
- the measurement path must expose separate responses for:
  - `P_small`
  - `P_large`
  - `N_small`
  - `N_large`

2. aggregate second
- compute signed contrast only after the four sector responses are available

3. diagnose third
- compute stability and collapse diagnostics after signed contrast is computed

## Why this matters
The ordering is the whole point.

If the pipeline becomes:
- state -> pooled scalar -> sign decision

then the pair-state angle has failed before the result is even analyzed.

The required ordering is:
- state -> sector responses -> signed contrast -> diagnostics

## Candidate rejection test
Reject the future implementation immediately if any of the following happen:
- sector responses are not separately observable in the diagnostic output
- signed contrast is computed from an already pooled scalar
- stability diagnostics cannot identify whether one sub-sector dominates the result

## Candidate acceptance condition at the design level
The pair-state direction becomes approval-worthy only if a future implementation plan can show:
1. each sector response is explicit
2. no irreversible pooling happens before contrast calculation
3. the diagnostic output can falsify sector imbalance and collapse

## Interaction with the content block
The content block may modulate sector responses.

It may not:
- replace them
- obscure them
- or force aggregation before sector resolution

So the content-encoding rule and measurement-realization rule must stay compatible.

## What this closes
This memo closes the second major gap from the readiness reassessment:
- low-level measurement realization rule

At the memo level, the pair-state direction now has:
- content-encoding rule
- sector scheme
- aggregation rule
- construction sketch
- measurement-operator family
- measurement-realization ordering rule

## Bottom line
The pair-state direction is now close to the maximum useful specificity that archive-safe memo work can provide.

The key rule is explicit:
- no pooling before sector resolution

That is the line that separates a credible future restart from another disguised proxy path.

