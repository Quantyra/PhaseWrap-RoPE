# Q-RoPE Transition Orbit Order-Margin Decision Memo v1

Date: 2026-03-11
Stories: S399

## Decision
- stop the execution branch
- return the line to memo-only posture

## Reason
- the approved branch rule declared two primary metrics:
  - mean absolute error
  - rank correlation
- the witness led on mean absolute error but failed the rank-correlation part of the gate
- failure was material, not marginal:
  - mean rank correlation was negative overall
  - two of three seeds were strongly negative

## Consequence
- do not widen this task
- do not add more controls to this task
- preserve only the next memo-only angle

## Preserved Signal
- the witness may still be useful for magnitude-like separation under this task
- it is not stable enough as an order-margin branch under the current gate
