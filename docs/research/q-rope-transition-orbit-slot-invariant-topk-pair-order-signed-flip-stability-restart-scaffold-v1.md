# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Flip Stability Restart Scaffold v1

Date: 2026-03-11
Stories: S600

## Future Candidate
- `V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_stability_invariant`

## Fixed Future Controls
- `V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_lookup`
- `V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_cross_direction`
- `V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_quadratic`
- `V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_orbit_permuted`

## Fixed First Packet
- dataset: `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit

## Intended Gate
- primary metrics:
  - `accuracy`
  - `F1`
- mixed leadership is not enough
- no remote work, task expansion, or control-family expansion is allowed in the first packet
