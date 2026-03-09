# Restart scaffold for chart-transition manifold task

## Task
- `synthetic_dual_chart_transition_manifold_response`

## Future candidate
- `V_future_relational_witness_chart_transition`

## Fixed future controls
- `V_control_symbolic_coarse_lookup_regressor`
- `V_control_symbolic_analog_only_regressor`
- `V_control_symbolic_nonlinear_manifold_regressor`
- `V_control_symbolic_phase_insensitive_regressor`
- `V_control_symbolic_global_phase_regressor`
- `V_control_symbolic_single_chart_regressor`
- `V_control_symbolic_transition_additive_regressor`

## Fixed first packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit

## Required diagnostics
- coarse tuple mean absolute max
- within-state variation flag
- candidate/control mean MAE
- candidate/control rank correlation
- proof that source and destination chart ids are not exposed to controls
- proof that the transition-additive control uses only declared analog factors plus one bounded ordered transition family

## Future gate
Do not approve implementation unless the task memo and scaffold together show all of the following:
- coarse lookup is near-null by construction
- additive analog baselines are intentionally insufficient
- the current nonlinear, phase-insensitive, bounded global-phase, and bounded single-chart families are intentionally insufficient
- one bounded ordered-transition additive symbolic control is intentionally insufficient
