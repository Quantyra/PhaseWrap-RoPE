# Q-RoPE Transfer Staggered Binding Implementation Plan v1

Date: 2026-03-13
Stories: S1019

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Fixed Task
- `synthetic_symbolic_insufficiency_staggered_binding_response`

## Fixed Models
- Witness:
  - `V_future_relational_witness_symbolic_insufficiency_staggered_binding`
- Control:
  - additive and bounded-quadratic regressor over declared source/stage/bind summaries only

## Fixed Packet
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`
  - `123`
  - `777`
- primary metrics:
  - `mae`
  - `rank_correlation`

## Required Audits
- generator hard-stop diagnostics must pass on every run
- witness:
  - `bounded_feature_audit_pass`
  - `forbidden_feature_family_absent_pass`
- control:
  - `allowed_staggered_binding_symbolic_basis_frozen_pass`
  - `forbidden_feature_family_absent_pass`

## Stop Rule
Stop the line immediately if the bounded control matches or beats the witness on both declared packet metrics.
