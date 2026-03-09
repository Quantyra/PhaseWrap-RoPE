# Local atlas manifold implementation

## Scope executed
- task: `synthetic_dual_local_atlas_manifold_response`
- candidate: `V_future_relational_witness_local_atlas`
- controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_nonlinear_manifold_regressor`
  - `V_control_symbolic_phase_insensitive_regressor`
  - `V_control_symbolic_global_phase_regressor`
  - `V_control_symbolic_single_chart_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Implementation summary
- added the local atlas manifold generator path in `src/qrope/synthetic.py`
- added one bounded witness path and one bounded single-chart symbolic control in `src/qrope/run.py`
- kept chart ids out of all controls by construction
- kept execution local-only and zero-credit

## Validation
- focused suite: `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- result: `141 passed`

## Artifacts
- packet summary: `logs/ablation_runs/summary/local_atlas_manifold_v1.csv`
- run artifacts under `logs/ablation_runs/atlas-*/`
