# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Rank-Only First Packet v1

Date: 2026-03-10
Status: complete
Story: S524

## Packet
- dataset: `synthetic_transition_orbit_slot_invariant_channel_order_topk_rank_only`
- backend: `sim_quantum_statevector`
- seeds: `42, 123, 777`
- candidate: `V_future_relational_witness_transition_orbit_channel_order_topk_rank_only_invariant`
- controls:
  - `V_control_symbolic_transition_channel_order_topk_rank_only_invariant_lookup`
  - `V_control_symbolic_transition_channel_order_topk_rank_only_invariant_cross_direction`
  - `V_control_symbolic_transition_channel_order_topk_rank_only_invariant_quadratic`
  - `V_control_symbolic_transition_channel_order_topk_rank_only_invariant_orbit_permuted`

## Generator Gate
- `latent_slot_invariance_pass = true` on all runs
- `latent_slot_max_abs_delta = 0` on all runs
- `slot_view_balance_pass = true` on all runs
- `coarse_slot_topk_rank_lookup_near_null_pass = true` on all runs
- `within_state_topk_rank_variation_pass = true` on all runs

## Packet Means
- witness: `accuracy = 0.151515`, `order_f1 = 0.344733`
- lookup: `accuracy = 0.000000`, `order_f1 = 0.000000`
- cross-direction: `accuracy = 0.181818`, `order_f1 = 0.315152`
- quadratic: `accuracy = 0.151515`, `order_f1 = 0.227706`
- orbit-permuted: `accuracy = 0.181818`, `order_f1 = 0.327273`

## Artifact
- summary: [transition_orbit_channel_order_topk_rank_only_invariant_v1.csv](C:/Users/Dan/Desktop/Projects/QuantyraQRope/logs/ablation_runs/summary/transition_orbit_channel_order_topk_rank_only_invariant_v1.csv)
