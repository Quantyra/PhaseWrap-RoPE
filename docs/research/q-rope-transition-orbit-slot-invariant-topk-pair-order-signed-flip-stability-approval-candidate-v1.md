# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Flip Stability Approval-Candidate v1

Date: 2026-03-11
Stories: S601

## Decision
- place the slot-invariant top-k pair-order signed-flip stability line at approval-candidate posture
- keep implementation closed in this step

## Why
- the line is materially different from the stopped signed-flip consistency branch
- it targets whether directional reversal remains stable across paired contexts rather than whether a flip occurs in the first place
- the control family is explicit and bounded

## Remaining Blocker
- the generator has not yet proven that coarse slot state and trivial paired-view collapse are weak enough that a bounded symbolic signed-flip stability baseline cannot win trivially

## Next Legitimate Move
- write the dedicated implementation-approval gate only if the slot-invariant signed-flip stability generator contract remains unchanged
