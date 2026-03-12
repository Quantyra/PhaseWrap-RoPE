# Q-RoPE Transfer Fork-Join Implementation Plan v1

Date: 2026-03-12
Stories: S914

## Goal
Define one bounded implementation cycle for the fork-join transfer line.

## Frozen Task
- `synthetic_symbolic_insufficiency_fork_join_response`

## Frozen Models
- witness:
  - `V_future_relational_witness_symbolic_insufficiency_fork_join`
- bounded control:
  - fork-join additive and bounded-quadratic regressor over declared fork-join summaries only

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
- exactly one packet only
- no second control family
- no widening to hardware or non-transfer tasks

## Required Generator Diagnostics
- `coarse_fork_state_null_pass`
- `within_fork_state_variation_pass`
- `latent_fork_diversity_pass`
- `branch_balance_pass`
- `rejoin_target_nontrivial_pass`
- `token_view_balance_pass`

## Required Audits
- `allowed_fork_symbolic_basis_frozen_pass`
- `forbidden_fork_feature_family_absent_pass`

## Decision Rule
- stop the line immediately if the bounded control matches or beats the witness on both declared packet metrics:
  - `mae`
  - `rank_correlation`
