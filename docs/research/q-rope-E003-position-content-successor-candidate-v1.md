# Q-RoPE E003 Position-Content Successor Candidate v1

## BLUF
- Candidate:
  - `synthetic_positional_content_gated_offset_selection_response`
- The candidate is admissible for memo-level screening only.
- It is materially different from the preserved position-only package because the correct candidate must satisfy both bounded content relevance and bounded positional offset structure.

## Candidate Outline
- one query anchor with a bounded query-content class
- a small bounded candidate set
- each candidate has:
  - a bounded content class
  - a bounded relative-offset relation to the query anchor
- exactly one candidate is correct because it satisfies:
  - the declared content-key relevance rule, and
  - the declared positional offset rule
- distractors are constructed so that:
  - some satisfy content only,
  - some satisfy position only,
  - and some satisfy neither

## Why This Candidate Is Different
Current preserved bounded survivors show that the witness can survive:
- fixed-cardinality positional selection
- dual-anchor positional consensus selection
- variable-cardinality positional selection

This candidate asks a different question:
- can the witness survive when correct selection requires composition of bounded position and bounded content rather than position alone?

## Admissibility Conditions
- content classes must stay tightly bounded and auditable
- symbolic control may not use raw token identity, latent ids, or slot identity
- the correct answer must genuinely require both content and position
- if content-only or position-only bounded controls can solve the task by construction, reject the candidate

## Decision Leverage
- success would materially strengthen the claim that Q-RoPE evidence is moving toward more realistic selection structure
- failure would justify treating the current package as a position-only evidence ceiling

## Next Step
- write the explicit memo-level gate
- keep implementation and execution closed
