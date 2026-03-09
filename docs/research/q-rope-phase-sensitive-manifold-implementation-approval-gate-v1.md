# Implementation approval gate for phase-sensitive manifold path

## Decision
- `APPROVE`
- scope: `strictly limited`

## Approved scope
- task: `synthetic_dual_phase_sensitive_manifold_response`
- candidate: `V_future_relational_witness_phase_sensitive`
- controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_nonlinear_manifold_regressor`
  - `V_control_symbolic_phase_insensitive_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit

## Required gate conditions
- coarse-centering diagnostics must be emitted
- phase-insensitive control must exclude state-conditioned phase offsets
- no additional tasks, candidates, or controls may be added in the implementation phase

## Disallowed
- remote execution
- benchmark expansion
- parallel branch work
- any second phase-sensitive witness candidate
- any control that uses lookup features or agreement-tuple one-hot features
