# Token-invariant chart-transition implementation-approval gate

## Decision
- `APPROVE`
- scope: `strictly limited`

## Approved scope
- task: `synthetic_chart_transition_token_invariant_response`
- candidate: `V_future_relational_witness_chart_transition_invariant`
- controls:
  - `V_control_symbolic_transition_additive_regressor`
  - `V_control_symbolic_transition_unordered_regressor`
  - `V_control_symbolic_transition_cross_direction_regressor`
  - `V_control_symbolic_transition_quadratic_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit

## Required invariance gate inside implementation
The implementation is only valid if the generator emits paired latent-state diagnostics showing:
- `latent_target_invariance_pass = true`
- `latent_render_pair_count > 0`
- `latent_target_max_abs_delta = 0`
- `token_view_balance_pass = true`

## Disallowed
- remote execution
- benchmark expansion
- additional controls
- second witness candidate
- packet expansion beyond the fixed first run
