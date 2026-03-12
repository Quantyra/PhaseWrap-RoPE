# Q-RoPE Transfer Loop-Closure Slot-Swap Hardening Plan v1

Date: 2026-03-11
Stories: S894

## Goal
Apply one bounded structural hardening packet to the active loop-closure transfer line.

## Fixed Perturbation
- `slot_swap = 1`

## Frozen Packet
- task:
  - `synthetic_symbolic_insufficiency_loop_closure_response`
- witness:
  - `V_future_relational_witness_symbolic_insufficiency_loop`
- control:
  - `V_control_symbolic_symbolic_insufficiency_loop_regressor`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`

## Decision Rule
- stop the line immediately if the bounded control matches or beats the witness on both:
  - `mae`
  - `rank_correlation`
