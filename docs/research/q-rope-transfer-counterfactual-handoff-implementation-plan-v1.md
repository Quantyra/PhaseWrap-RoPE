# Q-RoPE Transfer Counterfactual-Handoff Implementation Plan v1

## Scope
Implement exactly one bounded execution cycle for:
- task: `synthetic_symbolic_insufficiency_counterfactual_handoff_response`
- witness: `V_future_relational_witness_symbolic_insufficiency_counterfactual_handoff`
- bounded control: additive and bounded-quadratic regressor over declared `source`, `handoff`, `counterfactual`, and `resolve` summaries only

## Writable Files
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Fixed Packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- one witness packet
- one bounded control packet
- no extra challengers
- no hardware

## Required Audits
- generator hard-stop diagnostics must pass on all runs
- witness feature audit must pass
- control frozen symbolic basis audit must pass
- forbidden feature family must remain absent

## Stop Rule
- stop immediately if the bounded control matches or beats the witness on both:
  - `mae`
  - `rank_correlation`

## Out of Scope
- transfer family variants
- additional hardening packets until after first packet decision
- hardware
- publication work
