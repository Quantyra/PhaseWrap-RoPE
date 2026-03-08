# Q-RoPE Pair-State Content-Encoding Memo v1

## Status
- `memo-only`
- `archive-safe`
- `not approved for implementation`

## Goal
Close the content-encoding gap for `V_pairstate_relational` at the memo level.

## Candidate rule
Use an `ordered token-pair compositional encoding`:

- assign each token type a base content code
- build the pair content block from the ordered composition `(x_i, x_j)`
- require the composition to preserve:
  - token identity
  - pair order
  - same-token vs cross-token distinction

Conceptually:
- `Content(x_i, x_j) = Compose(TokenCode(x_i), TokenCode(x_j), order=i->j)`

## Why ordered composition matters
If pair order is lost, the content block can become symmetric in a way that weakens relational interpretation.

The future candidate should distinguish:
- `(A, B)` from `(B, A)`
- `(A, A)` from `(A, B)`

That is the minimum content structure needed to test whether offset sectors interact meaningfully with ordered token relations.

## Interaction with the sector block
The design intent is:
- sector block says where the pair belongs in signed offset space
- content block says what ordered pair occupies that sector
- coupling block tests whether ordered pair identity modulates sector response coherently

So the content block must not:
- determine the label by itself
- erase the sector structure
- collapse all ordered pairs into one pooled token-pair statistic

## Candidate anti-domination rule
Reject the future implementation if content encoding causes:
- sector responses to become nearly identical within sign classes regardless of offset block
- or the measured contrast to be explained primarily by token-pair identity rather than signed offset sectors

## Why this improves the pair-state angle
This closes one of the two major gaps from the readiness reassessment:
- the content block is no longer only a vague placeholder

Now the pair-state brief has:
- sector scheme
- aggregation rule
- construction sketch
- operator family
- explicit content-encoding intent

## What still remains open
The largest remaining gap is now:
- low-level realization of sector-resolved measurement without pooled-score collapse

## Bottom line
The pair-state direction now has a candidate content-encoding rule:
- ordered token-pair compositional encoding

That makes the preserved restart materially sharper on paper, even though it still does not authorize implementation.

