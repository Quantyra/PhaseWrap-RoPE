# Q-RoPE Core Scoring Redesign Plan v1

## Decision
Redesign the local scoring path around an explicit pairwise comparison primitive instead of a single-state proxy score.

Preferred redesign family:
- `pairwise-relative-overlap screening`

## Why this is the right redesign
The formalization and concept note both point to the core thesis:
- positional effect should emerge inside a query-key comparison
- relative offset should appear through `P(i)^dagger P(j)`

The current local path does not do that.
It turns one encoded state into a scalar score and then uses thresholding.

That proxy has been useful for screening infrastructure, but it is now the main technical bottleneck.

## Redesign target
Move from:
- single-state score `s(x)`

Toward:
- pairwise similarity score `K(x_i, x_j)`

Local-first approximation:
- build two states from two texts with shared positional-phase structure
- score them with a normalized overlap-like quantity from the statevector

This is not full quantum attention yet.
It is the closest local screening approximation to the original Q-RoPE mechanism that the current simulator can support cheaply.

## Minimal local design
Primary file:
- `src/qrope/qsim.py`

New capability:
- pairwise local score function, for example:
  - `pairwise_quantum_score(text_a, text_b, variant, seed, ...)`

Preferred local comparison form:
1. prepare state for `text_a`
2. prepare state for `text_b`
3. compute overlap-style similarity from the two final statevectors
4. use that similarity in a simple retrieval/classification proxy

Key rule:
- keep feature loading and positional phase family unchanged for the first redesign pass
- only change the scoring primitive

## Evaluation packet
Stay local and zero-credit.

Initial packet:
- backend: local statevector only
- variants:
  - `V0`
  - `V3`
- comparison:
  - current single-state proxy baseline
  - new pairwise-relative-overlap screening path
- datasets:
  - `yelp`
  - `imdb`
  - `amazon`

Keep the first packet small and diagnostic before scaling.

## Promotion gate
Carry the redesign forward only if it shows at least one of:
1. clearer `V3` vs `V0` separation than the current proxy path
2. lower seed-instability in the local diagnostic packet
3. a more interpretable relation between relative-phase construction and observed score behavior

If none of those appear:
- stop the redesign
- do not widen benchmark scope yet

## Out of scope
- remote execution
- new benchmark family as the main branch
- new variant creation
- deep architecture rewrite

## Recommended next implementation step
Implement a local pairwise-overlap helper and a tiny diagnostic packet comparing:
- `V0` vs `V3`
- single-state proxy vs pairwise-overlap score

## Bottom line
The next technical move should redesign the score itself, not another tail or threshold.
The right first pass is a local pairwise-relative-overlap screening path.
