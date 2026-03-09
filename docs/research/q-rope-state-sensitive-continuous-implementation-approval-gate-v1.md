# State-sensitive continuous implementation approval gate

## Decision
- `APPROVE`, but narrowly.

## Approved scope
- one local-only implementation phase
- one synthetic task: `synthetic_dual_state_sensitive_continuous_response`
- one candidate: `V_future_relational_witness_state_sensitive`
- three fixed controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_full_declared_regressor`
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
The path is specific enough to justify one bounded falsification cycle, and the prior continuous branch failed for a clear shortcut reason that this new task is designed to block.
