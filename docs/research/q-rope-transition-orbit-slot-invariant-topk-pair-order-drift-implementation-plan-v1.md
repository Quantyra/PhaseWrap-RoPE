# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Drift Implementation Plan v1

Date: 2026-03-11
Status: approved
Story: S567

## Goal
Implement one strictly bounded local synthetic packet for `synthetic_transition_orbit_slot_invariant_topk_pair_order_drift_response`.

## Allowed Changes
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Fixed Packet
- dataset:
  - `synthetic_transition_orbit_slot_invariant_topk_pair_order_drift_response`
- candidate:
  - `V_future_relational_witness_transition_orbit_topk_pair_order_drift_invariant`
- controls:
  - `V_control_symbolic_transition_topk_pair_order_drift_invariant_lookup`
  - `V_control_symbolic_transition_topk_pair_order_drift_invariant_cross_direction`
  - `V_control_symbolic_transition_topk_pair_order_drift_invariant_quadratic`
  - `V_control_symbolic_transition_topk_pair_order_drift_invariant_orbit_permuted`
- seeds:
  - `42`, `123`, `777`

## Decision Metrics
- `mae`
- `rank_correlation`

## Stop Condition
- stop the branch if the witness does not lead the fixed control stack on both declared metrics.
