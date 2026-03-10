# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Consistency Implementation Plan v1

Date: 2026-03-10
Stories: S504

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Fixed Packet
- task: `synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary`
- candidate: `V_future_relational_witness_transition_orbit_channel_order_topk_consistency_invariant`
- controls:
  - `V_control_symbolic_transition_channel_order_topk_consistency_invariant_lookup`
  - `V_control_symbolic_transition_channel_order_topk_consistency_invariant_cross_direction`
  - `V_control_symbolic_transition_channel_order_topk_consistency_invariant_quadratic`
  - `V_control_symbolic_transition_channel_order_topk_consistency_invariant_orbit_permuted`
- seeds: `42`, `123`, `777`

## Primary Metrics
- `accuracy`
- `f1`

## Required Outputs
- `run_diagnostics.json`
- generator hard-stop diagnostics
- packet summary csv

## Explicit Prohibitions
- no remote execution
- no benchmark expansion
- no control-family expansion
- no second witness candidate
