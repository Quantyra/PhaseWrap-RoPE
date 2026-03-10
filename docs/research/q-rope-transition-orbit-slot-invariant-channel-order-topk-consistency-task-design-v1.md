# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Consistency Task Design v1

Date: 2026-03-10
Stories: S499

## Preserved Next Angle
- future task: `synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary`

## Rationale
- the stopped rank-only branch preserved the strongest order-F1 signal but lost on top-level list accuracy
- the next legitimate continuation is to supervise top-k consistency under the same slot-invariance contract rather than reuse the same full-list ranking objective

## Contract
- keep slot identity a nuisance variable by construction
- keep bounded symbolic invariant top-k controls explicit
- remain memo-only until a new approval-candidate review is written
