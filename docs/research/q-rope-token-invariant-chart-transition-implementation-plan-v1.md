# Token-invariant chart-transition implementation plan

## Writable scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Required generator behavior
- build latent chart-transition states first
- render at least `identity` and `cdab` token views from the same latent states
- compute targets from latent chart-transition geometry only
- emit paired latent invariance diagnostics into dataset diagnostics

## Required candidate and control packet
- candidate: `V_future_relational_witness_chart_transition_invariant`
- controls:
  - `V_control_symbolic_transition_additive_regressor`
  - `V_control_symbolic_transition_unordered_regressor`
  - `V_control_symbolic_transition_cross_direction_regressor`
  - `V_control_symbolic_transition_quadratic_regressor`
- fixed seeds: `42`, `123`, `777`
- backend: `sim_quantum_statevector`

## Required stop rule
- stop immediately if latent-state invariance diagnostics fail
- otherwise run the fixed packet and decide the branch from MAE and rank-correlation only
