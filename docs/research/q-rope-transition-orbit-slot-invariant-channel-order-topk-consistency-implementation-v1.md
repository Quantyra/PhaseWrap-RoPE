# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Consistency Implementation v1

Date: 2026-03-10
Stories: S505

## Scope
- task: `synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary`
- candidate: `V_future_relational_witness_transition_orbit_channel_order_topk_consistency_invariant`
- controls:
  - `V_control_symbolic_transition_channel_order_topk_consistency_invariant_lookup`
  - `V_control_symbolic_transition_channel_order_topk_consistency_invariant_cross_direction`
  - `V_control_symbolic_transition_channel_order_topk_consistency_invariant_quadratic`
  - `V_control_symbolic_transition_channel_order_topk_consistency_invariant_orbit_permuted`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Validation
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- result: `204 passed`

## Generator Contract
- `latent_slot_invariance_pass = true` on all runs
- `latent_slot_max_abs_delta = 0` on all runs
- `coarse_slot_topk_lookup_near_null_pass = true` on all runs
- `within_state_topk_variation_pass = true` on all runs
