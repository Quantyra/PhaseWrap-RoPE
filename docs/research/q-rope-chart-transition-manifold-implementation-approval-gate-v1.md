# Chart-transition manifold implementation approval gate

## Decision
- approve one strictly bounded implementation phase

## Approved scope
- task: `synthetic_dual_chart_transition_manifold_response`
- candidate: `V_future_relational_witness_chart_transition`
- controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_nonlinear_manifold_regressor`
  - `V_control_symbolic_phase_insensitive_regressor`
  - `V_control_symbolic_global_phase_regressor`
  - `V_control_symbolic_single_chart_regressor`
  - `V_control_symbolic_transition_additive_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit

## Approval rationale
The task, future candidate, control stack, and packet are now specific enough to justify one falsifiable bounded implementation phase. The added transition-additive control raises the fairness bar beyond the failed local-atlas line while keeping the branch tightly scoped.

## Explicitly disallowed
- remote execution
- benchmark expansion
- source or destination chart-id exposure to any control
- second witness candidate
- packet expansion beyond the fixed first run
- uncontrolled symbolic basis growth
