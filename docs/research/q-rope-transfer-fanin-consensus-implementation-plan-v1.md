# Q-RoPE Transfer Fan-In Consensus Implementation Plan v1

## Frozen Scope
- Task: `synthetic_symbolic_insufficiency_fanin_consensus_response`
- Witness: `V_future_relational_witness_symbolic_insufficiency_fanin_consensus`
- Control: additive and bounded-quadratic regressor over declared fan-in consensus summaries only

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Fixed Packet
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- One witness vs one bounded symbolic control only

## Stop Rule
- Stop the line immediately if the control matches or beats the witness on both:
  - `mae`
  - `rank_correlation`
