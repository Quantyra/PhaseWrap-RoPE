# Q-RoPE E006 Multi-Hop Reference Plan Decision v1

Date: 2026-03-16
Stories: S1452-S1453

## BLUF
- `E006` passes only to one bounded local implementation cycle.
- This is the last planning barrier before code.
- The line should stop immediately if direct-collapse prevention cannot be maintained in implementation.

## Decision
- `PASS_TO_ONE_BOUNDED_IMPLEMENTATION_CYCLE`

## Why
- the multi-hop task remains materially different from direct selection and repeated shared-memory query reuse
- the frozen bounds are small enough to stay auditable
- the main scientific risk is direct-collapse, and the plan now makes that a hard-stop condition rather than a post hoc interpretation issue
