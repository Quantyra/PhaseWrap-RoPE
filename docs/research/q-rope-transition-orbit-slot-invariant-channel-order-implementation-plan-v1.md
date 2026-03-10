# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Implementation Plan v1

Date: 2026-03-10
Stories: S477

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Fixed Packet
- dataset: `synthetic_transition_orbit_slot_invariant_channel_order_response`
- candidate:
  - `V_future_relational_witness_transition_orbit_channel_order_invariant`
- controls:
  - `V_control_symbolic_transition_channel_order_invariant_lookup`
  - `V_control_symbolic_transition_channel_order_invariant_cross_direction`
  - `V_control_symbolic_transition_channel_order_invariant_quadratic`
  - `V_control_symbolic_transition_channel_order_invariant_orbit_permuted`
- seeds: `42`, `123`, `777`
- backend: `sim_quantum_statevector`

## Primary Metrics
- `accuracy`
- `f1`

## Required Outputs
- `metrics.json`
- `generator_diagnostics.json`
- `run_diagnostics.json`
- packet summary csv
- packet memo
- post-packet decision memo
