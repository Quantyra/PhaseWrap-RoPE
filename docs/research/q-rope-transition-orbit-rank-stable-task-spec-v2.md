# Transition Orbit Rank-Stable Task Spec v2

## Task
- `synthetic_transition_orbit_rank_band_response`

## Core target rule
- keep ordered orbit-transition structure fixed
- define a coarse orbit-transition state as the ordered pair of orbit transition families
- assign multiple ordinal target bands inside each coarse state using a within-state analog quantity:
  - `orbit_band_delta`
- target is the rank band induced by `orbit_band_delta` inside each coarse state, not the coarse state itself

## Required properties
- every coarse orbit-transition state must contain at least three ordinal bands
- ordinal band membership must not be recoverable from coarse state identity alone
- a bounded symbolic ordinal lookup over coarse orbit-transition state must be near-null by construction

## Required bounded control
- `V_control_symbolic_transition_orbit_rank_lookup`
- features restricted to coarse orbit-transition state only
- no analog inputs
- no uncontrolled basis expansion
