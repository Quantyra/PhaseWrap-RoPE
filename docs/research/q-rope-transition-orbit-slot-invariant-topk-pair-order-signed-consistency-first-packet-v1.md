# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Consistency First Packet v1

Date: 2026-03-11
Status: complete
Story: S587

## Packet
- Dataset: `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Candidate: `V_future_relational_witness_transition_orbit_topk_pair_order_signed_consistency_invariant`
- Controls:
  - `V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_lookup`
  - `V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_cross_direction`
  - `V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_quadratic`
  - `V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_orbit_permuted`

## Means
- Witness: `accuracy=0.515151`, `f1=0.250000`
- Lookup: `accuracy=0.454545`, `f1=0.625000`
- Cross-direction: `accuracy=0.636364`, `f1=0.333333`
- Quadratic: `accuracy=0.636364`, `f1=0.333333`
- Orbit-permuted: `accuracy=0.636364`, `f1=0.333333`

## Artifact
- `logs/ablation_runs/summary/transition_orbit_topk_pair_order_signed_consistency_invariant_v1.csv`
