# Q-RoPE E006 Multi-Hop Reference Implementation Plan v1

Date: 2026-03-16
Stories: S1452-S1453

## BLUF
- `E006` is approved only for one bounded local implementation cycle.
- The implementation must preserve genuine multi-hop dependency:
  - query -> intermediate -> target
- Stop immediately if the task collapses into direct query-to-target solvability or requires symbolic-family branching.

## Frozen Task
- dataset:
  - `synthetic_positional_intermediate_pointer_selection_response`
- witness:
  - `V_future_relational_witness_positional_intermediate_pointer_selection`
- bounded symbolic control:
  - `V_control_symbolic_positional_intermediate_pointer_selection_regressor`

## Frozen Bounds
- candidate counts:
  - `4`, `5`
- hop depth:
  - exactly `2`
- content-class bound:
  - `3`
- one frozen symbolic family across all allowed candidate counts

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

## Required Diagnostics
- `coarse_multi_hop_state_null_pass`
- `within_multi_hop_state_variation_pass`
- `first_hop_nontrivial_pass`
- `second_hop_nontrivial_pass`
- `direct_target_null_pass`
- `intermediate_criticality_pass`
- `candidate_set_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_candidate_count_pass`
- `multi_hop_noncollapse_pass`

## Hard-Stop Conditions
Stop `E006` immediately if implementation requires:
- direct query-to-target summaries that bypass the intermediate hop
- symbolic-family branching by candidate count or hop pattern
- latent pointer tables or direct target lookup families
- token-id or slot-id shortcuts
- candidate-count cap above `5`
- hop depth above `2`
- examples where the intermediate is not decision-critical

## Packet Rule
- Run exactly one fixed three-seed packet against the bounded witness/control pair.
- Stop immediately if the control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
