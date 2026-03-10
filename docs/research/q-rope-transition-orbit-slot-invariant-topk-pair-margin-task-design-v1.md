# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair Margin Task Design v1

Date: 2026-03-10
Status: memo-only
Story: S535

## Preserved Next Angle
- future task: `synthetic_transition_orbit_slot_invariant_topk_pair_margin_response`

## Rationale
- the stopped top-k preference branch failed as a binary classification task against bounded controls
- the next coherent continuation is to score margin between the preferred and competing top-k pair relations instead of classifying a hard binary preference label
- this is materially different from the stopped branch, not a relabel of the same target
