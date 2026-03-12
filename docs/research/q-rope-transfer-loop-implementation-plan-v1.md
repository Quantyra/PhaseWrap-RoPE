# Q-RoPE Transfer Loop-Closure Implementation Plan v1

Date: 2026-03-11
Stories: S883

## Goal
Define one bounded implementation cycle for the loop-closure transfer line.

## Frozen Task
- `synthetic_symbolic_insufficiency_loop_closure_response`

## Frozen Models
- witness:
  - `V_future_relational_witness_symbolic_insufficiency_loop`
- bounded control:
  - loop-local additive and bounded-quadratic regressor over declared loop summaries only

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
- `coarse_loop_state_null_pass`
- `within_loop_state_variation_pass`
- `latent_loop_diversity_pass`
- `token_view_balance_pass`
- `loop_length_balance_pass`
- `closure_target_nontrivial_pass`

## Required Audits
- `allowed_loop_symbolic_basis_frozen_pass`
- `forbidden_loop_feature_family_absent_pass`

## Decision Rule
- stop the line immediately if the bounded control matches or beats the witness on both declared packet metrics:
  - `mae`
  - `rank_correlation`
