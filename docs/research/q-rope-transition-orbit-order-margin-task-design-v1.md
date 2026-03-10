# Q-RoPE Transition Orbit Order Margin Task Design v1

Date: 2026-03-11
Stories: S391

## Preserved Direction
- future task id: `synthetic_transition_orbit_order_margin_response`
- posture: memo-only

## Rationale
- the stopped listwise branch still preserved stronger ordering signal than the retained controls
- but it failed as a top-1 listwise branch under deeper pair perturbation
- the smallest materially different continuation is to score order margin directly rather than top-1 rank selection

## Boundary
- do not reopen implementation on the stopped listwise task
- do not widen the current control family
- require a new restart scaffold before any future approval discussion
