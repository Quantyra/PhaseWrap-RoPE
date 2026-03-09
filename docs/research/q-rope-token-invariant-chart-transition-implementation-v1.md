# Token-Invariant Chart-Transition Implementation v1

## Scope
- Task: `synthetic_chart_transition_token_invariant_response`
- Candidate: `V_future_relational_witness_chart_transition_invariant`
- Controls:
  - `V_control_symbolic_transition_additive_regressor`
  - `V_control_symbolic_transition_unordered_regressor`
  - `V_control_symbolic_transition_cross_direction_regressor`
  - `V_control_symbolic_transition_quadratic_regressor`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`

## Implementation notes
- Added paired latent render generation in `src/qrope/synthetic.py` via `generate_chart_transition_token_invariant_response_bundle(...)`.
- Added task label mode `chart_transition_token_invariant_response`.
- Added invariant witness/control routing in `src/qrope/run.py`.
- Added invariant-specific feature builders and bounded symbolic control backends.
- Added loader support for `synthetic_chart_transition_token_invariant_response`.

## Gate status
- `latent_target_invariance_pass = true`
- `latent_render_pair_count = 64`
- `latent_target_max_abs_delta = 0.0`
- `token_view_balance_pass = true`

## Validation
- Focused suite: `155 passed`
