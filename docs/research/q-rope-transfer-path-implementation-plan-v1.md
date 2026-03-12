# Q-RoPE Transfer Path Implementation Plan v1

Date: 2026-03-11
Stories: S854

## Scope
Implement exactly one bounded transfer packet for:
- task:
  - `synthetic_symbolic_insufficiency_path_response`
- witness transfer candidate:
  - `V_future_relational_witness_symbolic_insufficiency_path`
- bounded symbolic transfer control:
  - path-local additive and bounded-quadratic symbolic regressor over declared path summaries only

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only:
  - `tests/test_synthetic.py`
  - `tests/test_run_real_mode.py`

## Fixed Packet
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- one witness candidate
- one bounded symbolic control
- no second transfer family
- no hardware execution
- no provider work

## Required Generator Diagnostics
- `coarse_path_state_null_pass`
- `within_path_state_variation_pass`
- `latent_path_diversity_pass`
- `token_view_balance_pass`
- `path_length_balance_pass`

## Required Audit Outputs
- `allowed_path_symbolic_basis_frozen_pass`
- `forbidden_path_feature_family_absent_pass`
- witness packet metrics:
  - `mae`
  - `rank_correlation`
  - `calibration_slope`
- control packet metrics:
  - `mae`
  - `rank_correlation`
  - `calibration_slope`

## Decision Rule
- stop immediately if generator hard-stop diagnostics fail
- after execution, stop the line if the bounded symbolic transfer control matches or beats the witness on both:
  - `mae`
  - `rank_correlation`

## Disallowed
- widening the symbolic family after code inspection
- adding recurrent/state-machine symbolic features
- latent id leakage in emitted text or control features
- any packet beyond the fixed three-seed run in this step
