# Q-RoPE Transfer Braid Implementation Plan v1

Date: 2026-03-12
Stories: S938

## Goal
Define one bounded implementation cycle for the braid-crossing transfer line.

## Frozen Task
- `synthetic_symbolic_insufficiency_braid_crossing_response`

## Frozen Models
- witness:
  - `V_future_relational_witness_symbolic_insufficiency_braid`
- bounded control:
  - braid-local additive and bounded-quadratic regressor over declared braid summaries only

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
- `coarse_braid_state_null_pass`
- `within_braid_state_variation_pass`
- `latent_braid_diversity_pass`
- `crossing_target_nontrivial_pass`
- `token_view_balance_pass`
- `channel_balance_pass`

## Required Audits
- `allowed_braid_symbolic_basis_frozen_pass`
- `forbidden_braid_feature_family_absent_pass`

## Decision Rule
- stop the line immediately if the bounded control matches or beats the witness on both declared packet metrics:
  - `mae`
  - `rank_correlation`
