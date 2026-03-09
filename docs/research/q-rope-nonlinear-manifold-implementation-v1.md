# Nonlinear manifold implementation

## Scope
- Implemented only the approved nonlinear manifold branch on `synthetic_dual_nonlinear_manifold_response`.
- Added one candidate:
  - `V_future_relational_witness_nonlinear`
- Added three fixed controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_full_declared_additive_regressor`

## Validation
- Focused suite passed:
  - `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
  - result: `128 passed`

## Packet outputs
- Summary: `logs/ablation_runs/summary/nonlinear_manifold_v1.csv`
- Candidate:
  - `logs/ablation_runs/nonlin-witness-s42/metrics.json`
  - `logs/ablation_runs/nonlin-witness-s123/metrics.json`
  - `logs/ablation_runs/nonlin-witness-s777/metrics.json`
- Controls:
  - `logs/ablation_runs/nonlin-coarse-s42/metrics.json`
  - `logs/ablation_runs/nonlin-coarse-s123/metrics.json`
  - `logs/ablation_runs/nonlin-coarse-s777/metrics.json`
  - `logs/ablation_runs/nonlin-analog-s42/metrics.json`
  - `logs/ablation_runs/nonlin-analog-s123/metrics.json`
  - `logs/ablation_runs/nonlin-analog-s777/metrics.json`
  - `logs/ablation_runs/nonlin-full-s42/metrics.json`
  - `logs/ablation_runs/nonlin-full-s123/metrics.json`
  - `logs/ablation_runs/nonlin-full-s777/metrics.json`
