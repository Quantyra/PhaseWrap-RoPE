# Q-RoPE E003 Position-Content Missing Question v1

## BLUF
- Next missing question:
  - can the witness survive bounded candidate selection when correctness depends on composing a positional offset rule with a bounded content-key relevance rule, rather than position alone?
- This is the next best question because it targets the main remaining gap between the current package and a more RoPE-like selection setting.
- Execution remains closed.

## Why This Question Is Missing
Current preserved evidence covers:
- bounded positional selection under fixed candidate count
- bounded positional selection under dual-anchor consensus
- bounded positional selection under variable candidate count and distractor insertion

Those results are stronger than the earlier bridge package, but they still mainly test position-only selection. The current package does not yet answer whether the witness survives when:
- positional structure is necessary,
- content-key relevance is also necessary,
- and neither dimension alone is sufficient to identify the correct candidate.

## Decision Leverage
If this question succeeds:
- the package gains stronger evidence that Q-RoPE-style signal can survive bounded position-content composition rather than only pure positional selection.

If this question fails:
- the current package becomes a more defensible ceiling for bounded position-only evidence, and we stop implying that a more realistic compositional path is near.

## Candidate Direction
- `synthetic_positional_content_gated_offset_selection_response`

## Why Not Another Existing Family
- not another transfer family
- not another abstract bridge
- not another realism-bridge retrieval variant
- not another fixed- or variable-cardinality position-only successor clone

## Next Step
- write one candidate sketch and gate sketch only
- keep implementation and execution closed
