# Q-RoPE E008 Exception Arbitration Plan Decision v1

Date: 2026-03-16

## BLUF
- The E008 candidate passes to one bounded local implementation cycle only.
- The implementation must preserve one frozen symbolic family across exception patterns.
- Any fairness blow-up or exception-lookup collapse stops the epic immediately.

## Decision
- `PASS_TO_BOUNDED_IMPLEMENTATION`

## Why
- the missing question remains materially different from direct selection, multi-hop resolution, and revision validity
- the bounded implementation plan now freezes the fairness contract tightly enough for one local cycle
- the next protocol-valid uncertainty is implementation cleanliness, not more memo branching
