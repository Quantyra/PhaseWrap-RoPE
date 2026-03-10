# Q-RoPE Transition Orbit Sign-Flip Contrast Approval-Candidate v1

Date: 2026-03-11
Stories: S430

## Decision
- place the sign-flip contrast line at approval-candidate posture
- keep implementation closed in this step

## Why
- the line is materially different from the stopped sign-consistency branch
- it replaces passive agreement supervision with explicit flip-versus-hold supervision under controlled perturbation
- the control family is explicit and bounded

## Remaining Blocker
- the generator has not yet proven that coarse transition state and trivial paired-view collapse are weak enough that a bounded symbolic flip baseline cannot win trivially

## Next Legitimate Move
- write the dedicated implementation-approval gate only if the sign-flip contrast generator contract remains unchanged
