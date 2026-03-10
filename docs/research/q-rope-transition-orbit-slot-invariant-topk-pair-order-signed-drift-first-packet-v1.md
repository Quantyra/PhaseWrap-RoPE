# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Drift First Packet v1

Date: 2026-03-11
Status: complete
Story: S578

## Packet
- Dataset: `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Candidate: `V_future_relational_witness_transition_orbit_topk_pair_order_signed_drift_invariant`
- Controls:
  - `V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_lookup`
  - `V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_cross_direction`
  - `V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_quadratic`
  - `V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_orbit_permuted`

## Means
- Witness: `mae=0.449757`, `rank_correlation=-0.001596`
- Lookup: `mae=0.500000`, `rank_correlation=0.000000`
- Cross-direction: `mae=0.495358`, `rank_correlation=0.464473`
- Quadratic: `mae=0.497178`, `rank_correlation=0.464473`
- Orbit-permuted: `mae=0.493315`, `rank_correlation=0.370618`

## Artifact
- `logs/ablation_runs/summary/transition_orbit_topk_pair_order_signed_drift_invariant_v1.csv`
