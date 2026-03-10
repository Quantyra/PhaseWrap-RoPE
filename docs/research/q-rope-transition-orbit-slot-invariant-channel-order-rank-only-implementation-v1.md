# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Rank-Only Implementation v1

Date: 2026-03-10
Stories: S496

## Scope
- task: `synthetic_transition_orbit_slot_invariant_channel_order_rank_only`
- candidate: `V_future_relational_witness_transition_orbit_channel_order_rank_only_invariant`
- controls:
  - `V_control_symbolic_transition_channel_order_rank_only_invariant_lookup`
  - `V_control_symbolic_transition_channel_order_rank_only_invariant_cross_direction`
  - `V_control_symbolic_transition_channel_order_rank_only_invariant_quadratic`
  - `V_control_symbolic_transition_channel_order_rank_only_invariant_orbit_permuted`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Validation
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- result: `201 passed`

## Generator Contract
- `latent_slot_invariance_pass = true` on all runs
- `latent_slot_max_abs_delta = 0` on all runs
- `coarse_slot_rank_lookup_near_null_pass = true` on all runs
- `within_state_rank_variation_pass = true` on all runs
