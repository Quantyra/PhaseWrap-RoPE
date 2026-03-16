# Q-RoPE E005 Shared-Memory Multi-Query Candidate v1

Date: 2026-03-15
Stories: S1424-S1426

## BLUF
- Proposed candidate:
  - `synthetic_positional_shared_memory_multi_query_selection_response`
- The task uses one bounded candidate memory and two bounded query prompts.
- Correctness depends on answering both queries correctly under one frozen fairness contract.

## Candidate Sketch
- one shared candidate set with bounded size
- two query prompts over the same candidate set
- each query specifies a bounded position-content rule
- the correct output is a paired retrieval response or paired score over the two selected targets
- distractors are active for both queries
- at least one same-class alias distractor remains active in the shared memory

## Why It Is Materially Different
- It is not another one-shot selection task.
- It requires reusing one bounded memory under multiple query conditions.
- It is closer to repeated attention-style access than the current preserved survivor set.

## Bounded Fairness Direction
- small fixed query count: `2`
- small candidate-count cap
- one frozen symbolic family across both query positions and all allowed candidate counts
- no per-query lookup tables
- no token-id or slot-id shortcuts
