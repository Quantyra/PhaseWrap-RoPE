# Orthogonalized continuous implementation approval gate

## Decision
- `APPROVE`, but narrowly.

## Approved scope
- one local-only implementation phase
- one synthetic task: `synthetic_dual_orthogonalized_continuous_response`
- one candidate: `V_future_relational_witness_orthogonalized`
- three fixed controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_full_declared_residual_regressor`
- seeds: `42`, `123`, `777`
- backend: `sim_quantum_statevector`
- zero-credit only

## Disallowed
- remote execution
- extra tasks
- extra variants
- benchmark expansion
- cloud spend

## Gate rationale
The branch is specific enough to justify one bounded falsification cycle, and the last continuous branches failed for clear shortcut reasons that this orthogonalized task is designed to suppress directly.
