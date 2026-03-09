# Transition Orbit Rank-Band Implementation Approval Gate v1

## Decision
- approve one strictly bounded implementation phase

## Approved scope
- task: `synthetic_transition_orbit_rank_band_response`
- candidate: `V_future_relational_witness_transition_orbit_rank`
- controls:
  - `V_control_symbolic_transition_orbit_rank_lookup`
  - `V_control_symbolic_transition_cross_direction_regressor`
  - `V_control_symbolic_transition_quadratic_regressor`
  - `V_control_symbolic_transition_orbit_permuted_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit

## Hard stop rule
- stop before packet interpretation unless task diagnostics prove:
  - `coarse_rank_lookup_near_null_pass = true`
  - `within_state_rank_band_count_min >= 3`
  - `rank_band_balance_pass = true`

## Disallowed
- remote execution
- benchmark expansion
- second witness candidate
- uncontrolled symbolic basis growth
- packet expansion beyond the fixed first run
