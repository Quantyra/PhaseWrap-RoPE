# Q-RoPE E009 Scope-Masking Successor Candidate v1

Date: 2026-03-16
Stories: S1543-S1545

## Candidate
- `synthetic_positional_scope_masked_reference_selection_response`

## Candidate Idea
- Build one bounded candidate memory with one active local scope and one inactive outer region.
- The query specifies the target-relevant positional-content pattern.
- At least one stronger apparent match must exist outside the active scope.
- Exactly one in-scope candidate may remain valid after scope masking.

## Why This Candidate
- It is materially different from:
  - direct bounded selection
  - revision discrimination
  - exception-conditioned arbitration
  - shared-memory repeated query reuse
- It tests bounded eligibility by local scope membership, not just by direct rule satisfaction.
