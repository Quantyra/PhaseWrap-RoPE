# Implementation approval gate for nonlinear manifold path

## Decision
- `APPROVE`
- scope: `strictly limited`

## Approved scope
- task: `synthetic_dual_nonlinear_manifold_response`
- candidate: `V_future_relational_witness_nonlinear`
- controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_full_declared_additive_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit

## Required gate conditions
- orthogonalization/centering diagnostics must be emitted
- additive control schemas must exclude nonlinear interaction terms
- no additional tasks or candidates may be added in the implementation phase

## Disallowed
- remote execution
- benchmark expansion
- parallel branch work
- nonlinear symbolic control additions in this phase
