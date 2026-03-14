# Q-RoPE Transfer Counterfactual-Handoff Slot-Swap Hardening Plan v1

## Packet
- Task: `synthetic_symbolic_insufficiency_counterfactual_handoff_response`
- Perturbation: `slot_swap=1`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`

## Retained Models
- `V_future_relational_witness_symbolic_insufficiency_counterfactual_handoff`
- `V_control_symbolic_symbolic_insufficiency_counterfactual_handoff_regressor`

## Stop Rule
- Stop the line immediately if the bounded symbolic control matches or beats the witness on both:
  - `mae`
  - `rank_correlation`
