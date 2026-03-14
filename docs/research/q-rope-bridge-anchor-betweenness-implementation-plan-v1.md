# Q-RoPE Bridge Anchor-Betweenness Implementation Plan v1

## Task
- `synthetic_positional_anchor_betweenness_response`

## Witness
- `V_future_relational_witness_positional_anchor_betweenness`

## Bounded Symbolic Control
- additive and bounded-quadratic regressor over declared anchor-relative betweenness summaries only

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Fixed Packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Required Audits
- `allowed_anchor_betweenness_symbolic_basis_frozen_pass`
- `forbidden_anchor_betweenness_feature_family_absent_pass`

## Execution Rule
- Reopen code for one bounded local implementation cycle only.
- Run exactly one fixed three-seed packet.
- Stop the line immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
