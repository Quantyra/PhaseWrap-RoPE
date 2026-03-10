# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Consistency Decision Memo v1

Date: 2026-03-11
Status: complete
Story: S588

## Decision
Stop the execution branch.

## Reason
The witness led neither declared primary classification metric across the bounded control stack. Multiple controls beat it on `accuracy`, and the lookup control beat it on `f1`. Under the approved two-metric gate, the branch does not survive.

## Outcome
- Stop `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary` as an execution branch.
- Preserve only a memo-level next angle.
- Do not reopen this task under the same signed-consistency objective.
