# Q-RoPE Transition Orbit Asymmetric Sign-Localization Approval-Candidate v1

Date: 2026-03-11
Stories: S439

## Decision
- place the asymmetric sign-localization line at approval-candidate posture
- keep implementation closed in this step

## Why
- the line is materially different from the stopped sign-flip contrast branch
- it replaces flip-versus-hold supervision with asymmetric channel-localization supervision
- the control family is explicit and bounded

## Remaining Blocker
- the generator has not yet proven that coarse transition state and trivial channel symmetry are weak enough that a bounded symbolic localization baseline cannot win trivially

## Next Legitimate Move
- write the dedicated implementation-approval gate only if the asymmetric localization generator contract remains unchanged
