# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Preference First Packet v1

Date: 2026-03-10
Status: complete
Story: S533

## Packet
- dataset: `synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary`
- backend: `sim_quantum_statevector`
- seeds: `42, 123, 777`
- candidate: `V_future_relational_witness_transition_orbit_channel_order_topk_preference_invariant`
- controls:
  - `V_control_symbolic_transition_channel_order_topk_preference_invariant_lookup`
  - `V_control_symbolic_transition_channel_order_topk_preference_invariant_cross_direction`
  - `V_control_symbolic_transition_channel_order_topk_preference_invariant_quadratic`
  - `V_control_symbolic_transition_channel_order_topk_preference_invariant_orbit_permuted`

## Generator Gate
- `latent_slot_invariance_pass = true` on all runs
- `latent_slot_max_abs_delta = 0` on all runs
- `slot_view_balance_pass = true` on all runs
- `coarse_slot_topk_preference_lookup_near_null_pass = true` on all runs
- `within_state_topk_preference_variation_pass = true` on all runs

## Packet Means
- witness: `accuracy = 0.515152`, `f1 = 0.250000`
- lookup: `accuracy = 0.454545`, `f1 = 0.625000`
- cross-direction: `accuracy = 0.636364`, `f1 = 0.333333`
- quadratic: `accuracy = 0.636364`, `f1 = 0.333333`
- orbit-permuted: `accuracy = 0.636364`, `f1 = 0.333333`

## Artifact
- summary: [transition_orbit_channel_order_topk_preference_invariant_v1.csv](C:/Users/Dan/Desktop/Projects/QuantyraQRope/logs/ablation_runs/summary/transition_orbit_channel_order_topk_preference_invariant_v1.csv)
