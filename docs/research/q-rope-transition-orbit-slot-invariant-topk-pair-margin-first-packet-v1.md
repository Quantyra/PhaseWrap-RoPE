# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Margin First Packet v1

Date: 2026-03-10
Status: complete
Story: S542

## Packet
- dataset: `synthetic_transition_orbit_slot_invariant_topk_pair_margin_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- candidate: `V_future_relational_witness_transition_orbit_topk_pair_margin_invariant`
- controls:
  - `V_control_symbolic_transition_topk_pair_margin_invariant_lookup`
  - `V_control_symbolic_transition_topk_pair_margin_invariant_cross_direction`
  - `V_control_symbolic_transition_topk_pair_margin_invariant_quadratic`
  - `V_control_symbolic_transition_topk_pair_margin_invariant_orbit_permuted`

## Mean Metrics
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
  - `mae = 0.497178`
  - `rank_correlation = 0.464473`
- orbit-permuted:
  - `mae = 0.493315`
  - `rank_correlation = 0.370618`

## Generator Status
- hard-stop diagnostics passed on all runs
