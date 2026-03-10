# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Preference Implementation Plan v1

Date: 2026-03-10
Status: approved
Story: S531

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Fixed Packet
- dataset: `synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary`
- candidate plus the fixed bounded control stack
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Primary Metrics
- `accuracy`
- `f1`

## Explicitly Disallowed
- remote execution
- benchmark expansion
- second witness candidate
- control-family expansion
- packet expansion beyond the fixed first run
