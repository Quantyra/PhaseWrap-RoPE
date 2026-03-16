# Q-RoPE E007 Reference Revision Candidate v1

Date: 2026-03-16

## BLUF
- Candidate direction:
  - `synthetic_positional_reference_revision_selection_response`
- The task is bounded, auditable, and materially different from both `E005` and `E006`.
- It is still memo-only.

## Candidate Sketch
- one bounded query prompt
- one bounded candidate memory
- at least one stale candidate and one revised candidate that share bounded structural similarity
- exactly one candidate is current under a declared revision-validity rule
- correctness requires selecting the valid revision rather than the stale analogue

## Why This Is Different
- not repeated multi-query reuse over shared memory
- not two-stage reference chaining through an intermediate candidate
- not simple content alias pressure
- this is bounded validity discrimination under stale/current competition

## Candidate Name
- `synthetic_positional_reference_revision_selection_response`
