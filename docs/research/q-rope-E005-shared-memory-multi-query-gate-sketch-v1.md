# Q-RoPE E005 Shared-Memory Multi-Query Gate Sketch v1

Date: 2026-03-15
Stories: S1424-S1426

## BLUF
- `E005` is admissible only if it stays genuinely shared-memory and multi-query.
- The candidate fails immediately if the two queries can be solved independently by per-query lookup families.
- Execution remains closed until a stricter gate is written.

## Required Gate Conditions
- one shared candidate memory per example
- exactly two bounded query prompts per example
- same candidate memory reused across both queries
- one frozen symbolic family across both query positions
- no per-query token lookup behavior
- no slot-identity shortcuts
- no symbolic-family branching by query order or candidate count

## Immediate Reject Conditions
- task decomposes into two unrelated single-query packets
- correctness can be solved by content-only lookup per query
- correctness can be solved by slot-only lookup per query
- symbolic control requires separate families for query one and query two
- candidate memory or query count expands beyond a small bounded cap
