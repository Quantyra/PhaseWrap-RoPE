# Q-RoPE E004 Content-Alias Successor Candidate v1

## BLUF
- Candidate:
  - `synthetic_positional_content_alias_disambiguation_response`
- The candidate is admissible for memo-level screening only.
- It is materially different from `E003` because multiple candidates must share the target content class, so the correct answer requires positional disambiguation under alias pressure.

## Candidate Outline
- one query anchor with a bounded target content class
- a small bounded candidate set
- at least two candidates share the target content class
- exactly one candidate is correct because it satisfies:
  - the declared content-class match, and
  - the declared positional offset rule
- alias distractors are constructed so that:
  - some satisfy content only
  - some satisfy position only
  - at least one same-content distractor remains position-wrong

## Why This Candidate Is Different
Current preserved bounded survivors show that the witness can survive:
- fixed-cardinality positional selection
- dual-anchor positional consensus selection
- variable-cardinality positional selection
- clean bounded position-content gating

This candidate asks a different question:
- can the witness survive when content is aliased and position must disambiguate among same-class candidates rather than simply confirm a unique class match?

## Admissibility Conditions
- content classes must stay tightly bounded and auditable
- symbolic control may not use raw token identity, latent ids, or slot identity
- at least one same-class distractor must remain active in every candidate set
- if content-only or slot-only bounded controls can solve the task by construction, reject the candidate

## Decision Leverage
- success would materially strengthen the claim that Q-RoPE evidence survives bounded content alias pressure
- failure would justify treating the current package as a clean-gating evidence ceiling

## Next Step
- write the explicit memo-level gate
- keep implementation and execution closed
