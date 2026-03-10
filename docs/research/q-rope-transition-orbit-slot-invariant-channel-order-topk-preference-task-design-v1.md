# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Preference Task Design v1

Date: 2026-03-10
Status: memo-only
Story: S526

## Preserved Next Angle
- future task: `synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary`

## Rationale
- the stopped top-k rank-only branch preserved stronger order structure than the bounded controls but failed on the declared top-level accuracy gate
- the next coherent continuation is to make top-k pairwise preference primary instead of full top-k rank structure
- this is materially different from the stopped branch, not a relabel of the same objective
