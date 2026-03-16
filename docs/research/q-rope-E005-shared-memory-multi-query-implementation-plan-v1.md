# Q-RoPE E005 Shared-Memory Multi-Query Implementation Plan v1

Date: 2026-03-15
Stories: S1429-S1430

## BLUF
- `synthetic_positional_shared_memory_multi_query_selection_response` passes only to one bounded local implementation cycle.
- The implementation must keep shared-memory reuse real across both queries while preserving one frozen symbolic family.
- Execution remains bounded to one fixed three-seed packet if and only if the implementation clears the hard-stop conditions below.

## Frozen Task
- task:
  - `synthetic_positional_shared_memory_multi_query_selection_response`
- witness:
  - `V_future_relational_witness_positional_shared_memory_multi_query_selection`
- bounded symbolic control:
  - additive and bounded-quadratic regressor over declared shared-memory summaries, per-candidate summaries, per-query summaries, and bounded aggregate cross-query ambiguity summaries only

## Frozen Bounds
- query count:
  - `2`
- candidate-count range:
  - `3`, `4`, `5`
- content-class bound:
  - `3`
- shared-memory reuse requirement:
  - the same candidate memory must remain active for both queries in every example
- active alias requirement:
  - at least one same-class distractor remains active somewhere in the shared memory for at least one query family

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Fixed Packet
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`

## Hard-Stop Conditions
Stop E005 immediately if implementation requires:
- separate symbolic families by query position or candidate count
- decomposition into two unrelated single-query packets
- content-only solvability by construction across both queries
- position-only solvability by construction across both queries
- raw token-identity shortcuts
- slot-identity shortcuts
- query count above `2`
- candidate-count cap above `5`
- content-class cap above `3`
- examples without genuine shared-memory reuse

## Required Diagnostics
- `coarse_shared_memory_state_null_pass`
- `within_shared_memory_state_variation_pass`
- `query_pair_nontrivial_pass`
- `query_one_only_null_pass`
- `query_two_only_null_pass`
- `joint_query_target_nontrivial_pass`
- `shared_candidate_set_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_candidate_count_pass`
- `bounded_query_count_pass`
- `cross_query_noncollapse_pass`
- `shared_memory_reuse_pass`

## Outcome Rule
- implement once
- run exactly one fixed three-seed packet only if the frozen fairness contract holds
- stop immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`
