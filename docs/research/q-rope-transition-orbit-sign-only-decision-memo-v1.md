# Q-RoPE Transition Orbit Sign-Only Decision Memo v1

Date: 2026-03-11
Stories: S417

## Decision
- stop the execution branch
- return the line to memo-only posture

## Reason
- the approved branch rule declared two primary metrics:
  - accuracy
  - F1
- the witness did not lead on either metric against the strongest symbolic controls
- tied accuracy with worse F1 is not enough to keep the branch active

## Consequence
- do not widen this task
- do not add more controls to this task
- preserve only one next memo-only angle
