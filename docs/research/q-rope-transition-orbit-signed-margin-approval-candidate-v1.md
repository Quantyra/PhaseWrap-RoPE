# Q-RoPE Transition Orbit Signed-Margin Approval-Candidate v1

Date: 2026-03-11
Stories: S403

## Decision
- place the signed-margin line at approval-candidate posture
- keep implementation closed in this step

## Why
- the line is materially different from the stopped unsigned order-margin branch
- it targets the exact unresolved failure mode:
  - magnitude signal survived better than directional ordering signal
- the control family is now explicit and bounded

## Remaining Blocker
- the generator has not yet proven that signed-margin means are centered tightly enough that a coarse symbolic lookup cannot win trivially

## Next Legitimate Move
- write the dedicated implementation-approval gate only if the signed-margin generator contract remains unchanged
