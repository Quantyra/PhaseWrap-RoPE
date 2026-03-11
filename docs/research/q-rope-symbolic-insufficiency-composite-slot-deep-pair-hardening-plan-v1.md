# Q-RoPE Symbolic Insufficiency Composite Slot-Deep-Pair Hardening Plan v1

Date: 2026-03-10
Stories: S682

## Goal
Run one bounded composite structural perturbation on `synthetic_symbolic_insufficiency_transition_response` without changing the frozen symbolic basis.

## Packet
- dataset: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- perturbations:
  - `slot_swap=1`
  - `pair_reindex=7`
- candidate: `V_future_relational_witness_symbolic_insufficiency`
- control: `V_control_symbolic_symbolic_insufficiency_regressor`

## Gate
- keep the branch active only if the witness still leads the frozen-basis symbolic control on both declared packet metrics
- if the composite perturbation is inert, record that explicitly and then move to a different perturbation family rather than stack more of the same
