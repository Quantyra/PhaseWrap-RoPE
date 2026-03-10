# Q-RoPE Transition Orbit Sign-Consistency Approval-Candidate v1

Date: 2026-03-11
Stories: S421

## Decision
- place the sign-consistency line at approval-candidate posture
- keep implementation closed in this step

## Why
- the line is materially different from the stopped sign-only branch
- it targets the remaining unresolved signal from that branch:
  - directional structure may be more stable across paired contexts than in a single local view
- the control family is explicit and bounded

## Remaining Blocker
- the generator has not yet proven that coarse transition state and trivial paired-view collapse are weak enough that a bounded symbolic consistency baseline cannot win trivially

## Next Legitimate Move
- write the dedicated implementation-approval gate only if the sign-consistency generator contract remains unchanged
