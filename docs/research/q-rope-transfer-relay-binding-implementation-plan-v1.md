# Q-RoPE Transfer Relay-Binding Implementation Plan v1

Date: 2026-03-12
Stories: S966

## Scope
This plan permits one bounded implementation cycle for the relay-binding transfer line and nothing more.

## Task
- `synthetic_symbolic_insufficiency_relay_binding_response`

## Witness
- `V_future_relational_witness_symbolic_insufficiency_relay_binding`

## Bounded Symbolic Control
- relay-local additive and bounded-quadratic regressor over declared source, relay, and bind summaries only

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Fixed Packet
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`
  - `123`
  - `777`
- exactly one packet:
  - witness vs bounded relay symbolic control

## Required Generator Diagnostics
- `coarse_relay_state_null_pass`
- `within_relay_state_variation_pass`
- `latent_relay_diversity_pass`
- `token_view_balance_pass`
- `relay_length_balance_pass`
- `binding_target_nontrivial_pass`

## Required Audits
### Witness
- `bounded_feature_audit_pass`
- `forbidden_feature_family_absent_pass`

### Control
- `allowed_relay_symbolic_basis_frozen_pass`
- `forbidden_relay_feature_family_absent_pass`

## Stop Rule
- stop immediately if the control matches or beats the witness on both:
  - `mae`
  - `rank_correlation`

## Out Of Scope
- hardware
- additional transfer families
- extra perturbation packets in this story
- symbolic family expansion beyond the frozen relay basis
