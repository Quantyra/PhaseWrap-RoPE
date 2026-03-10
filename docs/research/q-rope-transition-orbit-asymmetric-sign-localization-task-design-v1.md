# Q-RoPE Transition Orbit Asymmetric Sign-Localization Task Design v1

Date: 2026-03-11
Stories: S436

## Preserved Next Angle
- future task id: `synthetic_transition_orbit_asymmetric_sign_localization_binary`

## Rationale
- the stopped sign-flip contrast branch was too easy for bounded symbolic flip/hold controls
- the next line should ask not just whether a flip occurred, but whether the directional change localizes to one asymmetric perturbation channel versus another
- that is materially different from both sign-consistency and flip-versus-hold classification

## Guardrail
- keep the line memo-only until the asymmetric sign-localization task is specified exactly and bound to bounded symbolic localization controls
