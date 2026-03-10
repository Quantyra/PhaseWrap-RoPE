# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Drift Decision Memo v1

Date: 2026-03-11
Status: complete
Story: S579

## Decision
Stop the execution branch.

## Reason
The witness led on `mae` but lost the declared second primary metric, `rank_correlation`, to multiple bounded controls. Under the approved two-metric gate, mixed leadership is not sufficient.

## Outcome
- Stop `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response` as an execution branch.
- Preserve only a memo-level next angle.
- Do not reopen this task under the same signed-drift objective.
