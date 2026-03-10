# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Margin Task Design v1

Date: 2026-03-10
Stories: S508

## Preserved Next Angle
- future task: `synthetic_transition_orbit_slot_invariant_channel_order_topk_margin_response`

## Rationale
- the stopped top-k consistency branch preserved only a tie on accuracy and no usable F1 signal
- the next legitimate continuation is a bounded top-k separation target under the same slot-invariance contract rather than another binary consistency label

## Contract
- keep slot identity a nuisance variable by construction
- keep bounded symbolic invariant top-k controls explicit
- remain memo-only until a new approval-candidate review is written
