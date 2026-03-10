# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Margin First Packet v1

Date: 2026-03-10
Status: complete
Story: S515

## Packet
- dataset: `synthetic_transition_orbit_slot_invariant_channel_order_topk_margin_response`
- seeds: `42, 123, 777`
- backend: `sim_quantum_statevector`
- candidate: `V_future_relational_witness_transition_orbit_channel_order_topk_margin_invariant`
- controls:
  - `V_control_symbolic_transition_channel_order_topk_margin_invariant_lookup`
  - `V_control_symbolic_transition_channel_order_topk_margin_invariant_cross_direction`
  - `V_control_symbolic_transition_channel_order_topk_margin_invariant_quadratic`
  - `V_control_symbolic_transition_channel_order_topk_margin_invariant_orbit_permuted`

## Generator Gate
- `latent_slot_invariance_pass = true` on all runs
- `latent_slot_max_abs_delta = 0` on all runs
- `slot_view_balance_pass = true` on all runs
- `coarse_slot_topk_margin_lookup_near_null_pass = true` on all runs
- `within_state_topk_margin_variation_pass = true` on all runs

## Packet Means
- witness:
  - `mae = 0.449757`
  - `rank_correlation = -0.001596`
- lookup:
  - `mae = 0.500000`
  - `rank_correlation = 0.000000`
- cross-direction:
  - `mae = 0.495358`
  - `rank_correlation = 0.464473`
- quadratic:
  - `mae = 0.[REDACTED-RECEIPT-ID]78`
  - `rank_correlation = 0.464473`
- orbit-permuted:
  - `mae = 0.493315`
  - `rank_correlation = 0.370618`

## Artifact
- summary: [transition_orbit_channel_order_topk_margin_invariant_v1.csv](C:/Users/Dan/Desktop/Projects/QuantyraQRope/logs/ablation_runs/summary/transition_orbit_channel_order_topk_margin_invariant_v1.csv)
