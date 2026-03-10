# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Task Design v1

Date: 2026-03-10
Stories: S472

## Preserved Next Angle
- future task: `synthetic_transition_orbit_slot_invariant_channel_order_response`

## Rationale
- the active channel-order branch failed under `slot_swap=1`
- that means slot identity still carries too much task leverage in the current construction
- the next legitimate continuation is to make slot identity a nuisance variable by construction instead of treating it as a post hoc hardening perturbation

## Contract
- the future task must prove latent slot invariance before any implementation approval
- bounded symbolic controls must remain fixed and explicit
- the line stays memo-only until a new approval-candidate review is written
