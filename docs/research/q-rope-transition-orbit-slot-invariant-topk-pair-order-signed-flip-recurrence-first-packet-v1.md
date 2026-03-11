# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Flip Recurrence First Packet v1

Date: 2026-03-11
Stories: S623

## Packet
- task: `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary`
- candidate: `V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_recurrence_invariant`
- controls:
  - `V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_lookup`
  - `V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_cross_direction`
  - `V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_quadratic`
  - `V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_orbit_permuted`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Generator Status
- all hard-stop diagnostics passed on all runs

## Important Correction
- the first packet launch used the wrong override keys and fell back to `dataset=yelp`, `backend=sim_local`, `run.seed=42`
- that output was discarded and rerun with the correct keys:
  - `dataset.name`
  - `backend.name`
  - `run.seed`
- only the corrected packet counts as evidence

## Mean Results
- witness:
  - `accuracy = 0.515151`
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

## Artifact
- summary csv: `logs/ablation_runs/summary/transition_orbit_topk_pair_order_signed_flip_recurrence_invariant_v1.csv`
