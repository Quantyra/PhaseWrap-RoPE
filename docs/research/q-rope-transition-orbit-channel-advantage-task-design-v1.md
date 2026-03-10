# Q-RoPE Transition Orbit Channel-Advantage Task Design v1

Date: 2026-03-11
Stories: S445

## Preserved Next Angle
- future task id: `synthetic_transition_orbit_channel_advantage_response`

## Rationale
- the stopped asymmetric localization branch collapsed to zero positive-class F1 under a binary target
- the next line should supervise the signed margin between perturbation-channel effects rather than only which channel wins
- that is materially different from binary localization and should preserve directional asymmetry without forcing a brittle class split

## Guardrail
- keep the line memo-only until the channel-advantage task is specified exactly and bound to bounded symbolic channel-advantage controls
