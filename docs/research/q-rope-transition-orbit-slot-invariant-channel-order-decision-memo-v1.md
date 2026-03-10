# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Decision Memo v1

Date: 2026-03-10
Stories: S480

## Decision
- stop the slot-invariant channel-order execution branch

## Reason
- under the approved gate, both `accuracy` and `F1` are primary metrics
- the witness led on `accuracy`
- the bounded quadratic control led on `F1`
- mixed leadership is not enough to keep the branch active under protocol

## Consequence
- return the line to memo-only posture
- preserve the next angle only if it changes the objective family rather than retrying the same binary target
