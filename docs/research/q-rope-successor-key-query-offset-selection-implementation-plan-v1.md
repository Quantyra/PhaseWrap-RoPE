# Q-RoPE Successor Key-Query Offset Selection Implementation Plan v1

Date: 2026-03-14
Stories: S1268-S1269

## BLUF
- The successor candidate is bounded enough to permit one implementation plan.
- The writable scope stays narrow and familiar.
- Execution remains a single bounded packet if the plan is accepted.

## Task
- `synthetic_positional_key_query_offset_selection_response`

## Witness
- `V_future_relational_witness_positional_key_query_offset_selection`

## Bounded Symbolic Control
- additive and bounded-quadratic regressor over declared query-anchor and candidate-set summaries only

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Fixed Packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Required Hard-Stop Diagnostics
- `coarse_key_query_selection_state_null_pass`
- `within_key_query_selection_state_variation_pass`
- `candidate_set_nontrivial_pass`
- `target_selection_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_candidate_count_pass`

## Required Audits
- `allowed_key_query_selection_symbolic_basis_frozen_pass`
- `forbidden_key_query_selection_feature_family_absent_pass`

## Execution Rule
- Reopen code for one bounded local implementation cycle only.
- Run exactly one fixed three-seed packet.
- Stop the line immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.

## Candidate-Specific Risk
- If the candidate-set summaries force lookup blow-up or large-set dependence during implementation, stop the successor class rather than widening the scope.
