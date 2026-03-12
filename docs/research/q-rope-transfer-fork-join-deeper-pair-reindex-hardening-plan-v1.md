# Q-RoPE Transfer Fork-Join Deeper Pair-Reindex Hardening Plan v1

Date: 2026-03-12
Stories: S927

## Goal
Apply one deeper bounded structural hardening packet to the active fork-join transfer line.

## Fixed Perturbation
- `pair_reindex = 7`

## Frozen Packet
- task:
  - `synthetic_symbolic_insufficiency_fork_join_response`
- witness:
  - `V_future_relational_witness_symbolic_insufficiency_fork_join`
- control:
  - `V_control_symbolic_symbolic_insufficiency_fork_join_regressor`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`

## Decision Rule
- stop the line immediately if the bounded control matches or beats the witness on both:
  - `mae`
  - `rank_correlation`
