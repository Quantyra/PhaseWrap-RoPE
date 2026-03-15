# Q-RoPE E004 Content-Alias Missing Question v1

## BLUF
- Next missing question:
  - can the witness survive bounded candidate selection when multiple candidates share the same bounded content class and only the correct position-content composition identifies the target?
- This is the next best question because `E003` preserved clean bounded position-content composition, but not alias disambiguation under content collisions.
- Execution remains closed.

## Why This Question Is Missing
Current preserved evidence covers:
- bounded positional selection under fixed candidate count
- bounded positional selection under dual-anchor consensus
- bounded positional selection under variable candidate count and distractor insertion
- bounded position-content selection where the target satisfies both a bounded content rule and a bounded positional rule

Those results are stronger than the earlier package, but they still do not answer whether the witness survives when:
- at least two candidates share the target content class,
- content match alone is insufficient,
- and position must disambiguate under bounded alias pressure.

## Decision Leverage
If this question succeeds:
- the package gains stronger evidence that Q-RoPE-style signal survives bounded content collisions rather than only clean content gating.

If this question fails:
- the current package becomes a more defensible ceiling for bounded clean position-content evidence, and we stop implying alias-disambiguation capability.

## Candidate Direction
- `synthetic_positional_content_alias_disambiguation_response`

## Why Not Another Existing Family
- not another transfer family
- not another abstract bridge
- not another realism-bridge retrieval variant
- not another clean position-only or clean position-content successor clone

## Next Step
- write one candidate sketch and gate sketch only
- keep implementation and execution closed
