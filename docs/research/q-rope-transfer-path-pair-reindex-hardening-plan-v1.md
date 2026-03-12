# Q-RoPE Transfer Path Pair-Reindex Hardening Plan v1

Date: 2026-03-11
Stories: S862

## Plan
Run one bounded structural hardening packet with:
- task:
  - `synthetic_symbolic_insufficiency_path_response`
- perturbation:
  - `pair_reindex = 1`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`

## Compared
- `V_future_relational_witness_symbolic_insufficiency_path`
- `V_control_symbolic_symbolic_insufficiency_path_regressor`

## Decision Rule
- stop the branch immediately if the control matches or beats the witness on both:
  - `mae`
  - `rank_correlation`
