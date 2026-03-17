# Q-RoPE E010 Nested-Scope Shadow Implementation Plan v1

Date: 2026-03-17
Stories: S1580-S1581

## BLUF
- `E010` passes only to one bounded local implementation cycle.
- The task stays fixed at bounded nested-scope shadow precedence with one frozen symbolic family.
- Any collapse into flat masking or explicit scope lookup is an immediate stop.

## Frozen Task
- `synthetic_positional_nested_scope_shadow_selection_response`

## Frozen Witness
- `V_future_relational_witness_positional_nested_scope_shadow_selection`

## Frozen Symbolic Control
- `V_control_symbolic_positional_nested_scope_shadow_selection_regressor`

## Allowed Bounds
- candidate counts: `4`, `5`
- nested active scope count: exactly `2`
- content-class bound: `3`
- locally eligible candidate count before shadow precedence: exactly `2`
- final valid candidate count after shadow precedence: exactly `1`

## Frozen Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Fixed Packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Hard-Stop Conditions
- stop immediately if implementation requires:
  - explicit scope-id lookup tables
  - symbolic-family branching by candidate count or shadow pattern
  - token-id shortcuts
  - slot-id shortcuts
  - candidate-count cap above `5`
  - content-class cap above `3`
  - examples without two locally eligible candidates in nested active scopes
  - examples where nearer-scope precedence is not decision-critical
  - collapse into flat scope masking
  - content-only solvability by construction
  - position-only solvability by construction
