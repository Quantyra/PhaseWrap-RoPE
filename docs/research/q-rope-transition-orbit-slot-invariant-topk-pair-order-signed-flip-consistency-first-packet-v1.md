# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Flip Consistency First Packet v1

Date: 2026-03-11
Stories: S596

## Packet
- dataset: `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- candidate:
  - `V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_consistency_invariant`
- controls:
  - `V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_lookup`
  - `V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_cross_direction`
  - `V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_quadratic`
  - `V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_orbit_permuted`

## Generator Status
- all hard-stop diagnostics passed on all runs

## Packet Means
- witness:
  - `accuracy = 0.515152`
  - `f1 = 0.250000`
- lookup:
  - `accuracy = 0.454545`
  - `f1 = 0.625000`
- cross-direction:
  - `accuracy = 0.636364`
  - `f1 = 0.333333`
- quadratic:
  - `accuracy = 0.636364`
  - `f1 = 0.333333`
- orbit-permuted:
  - `accuracy = 0.636364`
  - `f1 = 0.333333`

## Summary Artifact
- `logs/ablation_runs/summary/transition_orbit_topk_pair_order_signed_flip_consistency_invariant_v1.csv`
