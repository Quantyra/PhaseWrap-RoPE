# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Flip Hysteresis Implementation Plan v1

Date: 2026-03-11
Stories: S639

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Fixed Packet
- dataset:
  - `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- candidate plus approved bounded controls only

## Decision Rule
- decide the branch from `accuracy` and `F1` only
- mixed leadership is not enough to keep the branch active

## Status
- approved implementation plan
- no expansion beyond fixed packet
