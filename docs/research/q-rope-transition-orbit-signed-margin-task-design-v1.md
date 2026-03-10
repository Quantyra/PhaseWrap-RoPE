# Q-RoPE Transition Orbit Signed-Margin Task Design v1

Date: 2026-03-11
Stories: S400

## Preserved Next Angle
- future task id: `synthetic_transition_orbit_signed_margin_response`

## Rationale
- the stopped order-margin branch preserved lower MAE but failed rank correlation
- that suggests the remaining unresolved question is directional margin structure, not unsigned gap size
- the next task should make signed direction the primary target instead of raw top-two gap magnitude

## Guardrail
- keep the line memo-only until the signed-margin task is specified exactly and bound to explicit bounded symbolic controls
