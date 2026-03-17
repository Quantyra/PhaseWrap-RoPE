# Q-RoPE E010 Nested-Scope Shadow Missing Question v1

Date: 2026-03-17
Stories: S1575-S1577

## BLUF
- The next missing question is whether the witness can survive bounded reference selection when multiple locally eligible candidates remain and the correct answer depends on nested-scope shadow precedence.

## Question
- Can the witness survive a bounded task where two candidates satisfy the same positional-content rule within nested active scopes, but only the candidate in the nearer active scope is valid after shadow precedence is applied?

## Why This Is Next
- `E009` established bounded local-scope eligibility masking.
- It did not test precedence among multiple locally eligible scoped candidates.
- Success or failure here would change whether the current package can be read as supporting bounded hierarchical scope control rather than only flat scope filtering.
