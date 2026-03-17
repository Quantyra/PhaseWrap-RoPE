# Q-RoPE E008 Exception Arbitration Implementation Plan v1

Date: 2026-03-16

## BLUF
- `E008` passes only to one bounded local implementation cycle.
- The plan freezes a single exception-conditioned symbolic family across all allowed candidate patterns.
- Execution remains bounded to one fixed three-seed packet if implementation is reopened under this plan.

## Frozen Task
- task:
  - `synthetic_positional_exception_conditioned_reference_selection_response`
- witness:
  - `V_future_relational_witness_positional_exception_conditioned_reference_selection`
- bounded symbolic control:
  - `V_control_symbolic_positional_exception_conditioned_reference_selection_regressor`

## Frozen Bounds
- candidate counts:
  - `4`, `5`
- content-class bound:
  - `3`
- exception count:
  - exactly `1` active exception clause per accepted example
- base-valid candidates:
  - exactly `1` default-valid candidate before exception application
- final-valid candidates:
  - exactly `1` surviving target after exception application

## Symbolic Family Limit
- additive and bounded-quadratic regressor over:
  - declared query summaries
  - per-candidate bounded content summaries
  - per-candidate bounded offset summaries
  - one bounded exception-trigger summary
  - bounded aggregate arbitration summaries only
- not allowed:
  - explicit exception ids
  - token-id shortcuts
  - slot-id shortcuts
  - per-exception-pattern symbolic families
  - disguised stale/current revision features

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

## Hard-Stop Conditions
Stop `E008` immediately if implementation requires:
- explicit exception lookup tables
- symbolic-family branching by candidate count or exception pattern
- token-id shortcuts
- slot-id shortcuts
- candidate-count cap above `5`
- content-class cap above `3`
- more than one active exception clause per example
- examples where the exception is not decision-critical
- content-only solvability by construction
- position-only solvability by construction
