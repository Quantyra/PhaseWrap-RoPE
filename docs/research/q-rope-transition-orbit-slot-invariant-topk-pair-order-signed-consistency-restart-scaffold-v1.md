# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Consistency Restart Scaffold v1

Date: 2026-03-11
Stories: S582

## Future Task
- `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary`

## Future Candidate
- `V_future_relational_witness_transition_orbit_topk_pair_order_signed_consistency_invariant`

## Fixed Future Controls
- `V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_lookup`
- `V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_cross_direction`
- `V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_quadratic`
- `V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_orbit_permuted`

## Fixed First Packet
- seeds: `42`, `123`, `777`
- backend: `sim_quantum_statevector`
- local-only
- zero-credit

## Primary Metrics
- accuracy
- F1

## Hard Stop Contract
- do not approve implementation until the task proves:
  - `latent_slot_invariance_pass = true`
  - `latent_slot_max_abs_delta = 0`
  - `slot_view_balance_pass = true`
  - `coarse_slot_topk_pair_signed_consistency_lookup_near_null_pass = true`
  - `within_state_topk_pair_signed_consistency_variation_pass = true`
  - `paired_context_diversity_pass = true`
  - `signed_consistency_label_balance_pass = true`

## Explicitly Disallowed
- reopening the failed signed-drift task
- remote execution
- benchmark expansion
- new symbolic control families
- second witness candidate
