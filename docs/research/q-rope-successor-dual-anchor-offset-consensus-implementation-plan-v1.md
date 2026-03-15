# Q-RoPE Successor Dual-Anchor Offset Consensus Implementation Plan v1

Date: 2026-03-14
Stories: S1300-S1301

## BLUF
- The dual-anchor consensus candidate is bounded enough to permit one implementation plan.
- The writable scope stays narrow and familiar.
- Execution remains closed until this bounded plan is explicitly accepted.

## Task
- `synthetic_positional_dual_anchor_offset_consensus_response`

## Witness
- `V_future_relational_witness_positional_dual_anchor_offset_consensus`

## Bounded Symbolic Control
- additive and bounded-quadratic regressor over declared dual-anchor summaries, per-candidate summaries, and bounded aggregate consensus summaries only

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Fixed Packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Required Hard-Stop Diagnostics
- `coarse_dual_anchor_consensus_state_null_pass`
- `within_dual_anchor_consensus_state_variation_pass`
- `candidate_set_nontrivial_pass`
- `dual_anchor_target_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_candidate_count_pass`
- `dual_anchor_noncollapse_pass`

## Required Audits
- `allowed_dual_anchor_consensus_symbolic_basis_frozen_pass`
- `forbidden_dual_anchor_consensus_feature_family_absent_pass`

## Execution Rule
- Reopen code for one bounded local implementation cycle only if this plan is accepted.
- Run exactly one fixed three-seed packet.
- Stop the line immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.

## Candidate-Specific Risk
- If the implementation requires explicit cross-anchor x candidate lookup structure or effectively collapses to single-anchor scoring, stop the candidate rather than widening the scope.
