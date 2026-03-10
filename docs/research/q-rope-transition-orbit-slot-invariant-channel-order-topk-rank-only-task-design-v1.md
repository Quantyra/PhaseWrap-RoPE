# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Rank-Only Task Design v1

Date: 2026-03-10
Status: memo-only
Story: S517

## Preserved Next Angle
- future task: `synthetic_transition_orbit_slot_invariant_channel_order_topk_rank_only`

## Rationale
- the stopped top-k margin branch preserved the best `mae` signal but failed on rank structure
- the next coherent continuation is to make top-k rank structure primary and remove top-k margin magnitude from the supervised target
- this is materially different from the stopped top-k margin branch, not a relabel of the same target

## Protocol Constraint
- memo-only until a new approval-candidate review is explicit
