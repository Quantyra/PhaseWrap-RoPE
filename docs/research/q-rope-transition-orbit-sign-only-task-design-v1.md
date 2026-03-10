# Q-RoPE Transition Orbit Sign-Only Task Design v1

Date: 2026-03-11
Stories: S409

## Preserved Next Angle
- future task id: `synthetic_transition_orbit_sign_only_binary`

## Rationale
- the stopped signed-margin branch preserved the strongest directional signal in the packet
- the remaining unresolved question is now sign prediction itself, not signed magnitude calibration
- the next task should make sign the primary target directly instead of mixing sign and magnitude again

## Guardrail
- keep the line memo-only until the sign-only task is specified exactly and bound to explicit bounded symbolic sign controls
