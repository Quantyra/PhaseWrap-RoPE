# Latent phase manifold implementation

## Scope executed
- task: `synthetic_dual_latent_phase_manifold_residual_response`
- candidate: `V_future_relational_witness_latent_phase`
- controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_nonlinear_manifold_regressor`
  - `V_control_symbolic_phase_insensitive_regressor`
  - `V_control_symbolic_global_phase_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Implementation summary
- added the latent phase manifold generator path in `src/qrope/synthetic.py`
- added one bounded witness path and one bounded global-phase symbolic control in `src/qrope/run.py`
- kept latent neighborhood ids out of all controls by construction
- kept execution local-only and zero-credit

## Validation
- focused suite: `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- result: `137 passed`

## Artifacts
- packet summary: `logs/ablation_runs/summary/latent_phase_manifold_v1.csv`
- run artifacts under `logs/ablation_runs/latent-*/`
