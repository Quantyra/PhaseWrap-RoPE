# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Flip Stability Task Design v1

Date: 2026-03-11
Stories: S598

## Preserved Next Angle
- `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary`

## Rationale
- the stopped signed-flip consistency branch asked whether directional reversal holds across paired contexts
- the next smallest materially different continuation is to test whether signed-flip order remains stable under paired context perturbation rather than just whether a flip occurs
- this preserves the slot-invariance contract while changing the supervised object enough to avoid reopening the same failed classification target under a new name

## Boundaries
- memo-only
- no implementation or experiment work reopened in this step
