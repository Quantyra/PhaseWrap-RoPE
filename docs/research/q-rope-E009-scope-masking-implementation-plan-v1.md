# Q-RoPE E009 Scope-Masking Implementation Plan v1

Date: 2026-03-16

## BLUF
- `E009` passes only to one bounded local implementation cycle.
- The plan freezes a single scope-conditioned symbolic family across all allowed candidate patterns.
- Execution remains bounded to one fixed three-seed packet if implementation is reopened under this plan.

## Frozen Task
- task:
  - `synthetic_positional_scope_masked_reference_selection_response`
- witness:
  - `V_future_relational_witness_positional_scope_masked_reference_selection`
- bounded symbolic control:
  - `V_control_symbolic_positional_scope_masked_reference_selection_regressor`

## Frozen Bounds
- candidate counts:
  - `4`, `5`
- content-class bound:
  - `3`
- scope count:
  - exactly `1` active local scope and `1` inactive outer region per accepted example
- in-scope validity:
  - exactly `1` final valid in-scope target per accepted example
- out-of-scope pressure:
  - at least `1` out-of-scope distractor with stronger apparent base positional-content fit than the final in-scope target

## Symbolic Family Limit
- additive and bounded-quadratic regressor over:
  - declared query summaries
  - per-candidate bounded content summaries
  - per-candidate bounded positional summaries
  - one bounded in-scope eligibility summary
  - bounded aggregate scope-competition summaries only
- not allowed:
  - explicit scope ids
  - direct in-scope/out-of-scope label lookup features
  - token-id shortcuts
  - slot-id shortcuts
  - scope-pattern-specific symbolic families

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
Stop `E009` immediately if implementation requires:
- explicit scope lookup tables
- symbolic-family branching by candidate count or scope pattern
- token-id shortcuts
- slot-id shortcuts
- candidate-count cap above `5`
- content-class cap above `3`
- examples without an out-of-scope stronger distractor
- examples where local scope is not decision-critical
- content-only solvability by construction
- position-only solvability by construction
