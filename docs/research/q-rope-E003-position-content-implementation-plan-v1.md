# Q-RoPE E003 Position-Content Implementation Plan v1

Date: 2026-03-14
Stories: S1364-S1365

## BLUF
- The position-content candidate is bounded enough to permit one implementation plan.
- The fairness contract remains strict: one frozen symbolic family must cover the allowed candidate family without content-only, position-only, count-specific, or class-specific basis drift.
- Execution remains closed until this bounded plan is explicitly accepted.

## Task
- `synthetic_positional_content_gated_offset_selection_response`

## Witness
- `V_future_relational_witness_positional_content_gated_offset_selection`

## Bounded Symbolic Control
- additive and bounded-quadratic regressor over declared query summaries, per-candidate content summaries, per-candidate offset summaries, and bounded aggregate ambiguity summaries only

## Frozen Candidate Family
- allowed active candidate counts: `3`, `4`, `5`
- fixed upper cap: `5`
- bounded content-class set size: `3`
- no implementation is allowed to widen either bound inside the plan

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Fixed Packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Required Hard-Stop Diagnostics
- `coarse_position_content_state_null_pass`
- `within_position_content_state_variation_pass`
- `content_only_null_pass`
- `position_only_null_pass`
- `joint_target_nontrivial_pass`
- `candidate_set_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_content_class_pass`
- `bounded_candidate_count_pass`
- `joint_noncollapse_pass`

## Required Audits
- `allowed_position_content_symbolic_basis_frozen_pass`
- `forbidden_position_content_feature_family_absent_pass`
- `single_symbolic_family_across_candidate_family_pass`

## Execution Rule
- Reopen code for one bounded local implementation cycle only if this plan is accepted.
- Run exactly one fixed three-seed packet.
- Stop the line immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.

## Candidate-Specific Hard Stop
Stop `E003` immediately if any of the following happen during implementation:
- the task is solvable by bounded content-only summaries by construction
- the task is solvable by bounded position-only summaries by construction
- the symbolic control needs separate families for candidate count or content class
- content relevance collapses into raw token-identity shortcuts
- the candidate-count cap must grow beyond `5` or the content-class cap beyond `3` to remain nontrivial
