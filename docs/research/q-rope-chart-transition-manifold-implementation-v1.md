# Chart-transition manifold implementation

## Scope executed
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

## Implementation summary
- added the chart-transition manifold generator path in `src/qrope/synthetic.py`
- added one bounded witness path and one bounded transition-additive symbolic control in `src/qrope/run.py`
- kept source and destination chart ids out of all controls by construction
- kept execution local-only and zero-credit

## Validation
- focused suite: `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- result: `145 passed`

## Artifacts
- packet summary: `logs/ablation_runs/summary/chart_transition_manifold_v1.csv`
- run artifacts under `logs/ablation_runs/transition-*/`
