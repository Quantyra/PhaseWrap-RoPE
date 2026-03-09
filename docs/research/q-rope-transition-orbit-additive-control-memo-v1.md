# Transition Orbit Additive Control Memo v1

## Purpose
Define the missing fairness baseline for `synthetic_chart_transition_orbit_response`.

## Control
- `V_control_symbolic_transition_orbit_additive_regressor`

## Allowed inputs
- orbit-canonical transition backbone
- orbit-canonical transition phase term
- orbit-canonical transition curvature term

## Forbidden inputs
- raw token identity
- token-view one-hot indicators
- unordered orbit lookup tables
- cross-family interaction terms
- quadratic or higher basis expansion in this control

## Role
This is the minimum additive symbolic baseline that matches the future task's declared orbit-level factors without escalating into a broader symbolic family.
