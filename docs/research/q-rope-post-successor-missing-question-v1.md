# Q-RoPE Post-Successor Missing Question v1

Date: 2026-03-14
Stories: S1295-S1297

## BLUF
- The next missing question is not another single-query offset-selection variant.
- The next real uncertainty is whether the witness signal can survive bounded positional selection when the correct answer must satisfy two positional constraints at once.
- If that cannot be specified cleanly under bounded fairness, the current package should be treated as the practical ceiling.

## Missing Question
- Can one bounded post-successor task be defined such that success would materially increase confidence that the witness signal survives compositional positional disambiguation rather than only single-query bounded selection, while failure would justify treating the current successor package as the practical evidence ceiling?

## Why This Is The Right Missing Question
- `offset-retrieval` answered bounded retrieval under distractor competition.
- `key-query-offset-selection` answered bounded one-of-many query-conditioned selection.
- What remains untested is whether the signal survives when positional correctness depends on satisfying two bounded positional constraints together, not just one.

## Why This Is Decision-Relevant
If the answer is yes:
- the internal case strengthens from bounded selection relevance to bounded compositional positional disambiguation.

If the answer is no:
- the current package likely marks the useful ceiling for the positional-relevance line without much more realistic model evidence.

## What Does Not Count As An Answer
- another same-family key-query selection variant
- a larger candidate-set version of the same task
- a loose transformer surrogate
- an uncontrolled benchmark jump

## Next Memo-Level Direction
- candidate class:
  - `synthetic_positional_dual_anchor_offset_consensus_response`
