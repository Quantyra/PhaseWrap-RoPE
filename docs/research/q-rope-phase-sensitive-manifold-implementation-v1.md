# Phase-sensitive manifold implementation

## Scope
- Implemented only the approved phase-sensitive manifold branch on `synthetic_dual_phase_sensitive_manifold_response`.
- Added one candidate:
  - `V_future_relational_witness_phase_sensitive`
- Added four fixed controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_nonlinear_manifold_regressor`
  - `V_control_symbolic_phase_insensitive_regressor`

## Validation
- Focused suite passed:
  - `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
  - result: `133 passed`

## Packet outputs
- Summary: `logs/ablation_runs/summary/phase_sensitive_manifold_v1.csv`
- Candidate:
  - `logs/ablation_runs/phase-witness-s42/metrics.json`
  - `logs/ablation_runs/phase-witness-s123/metrics.json`
  - `logs/ablation_runs/phase-witness-s777/metrics.json`
- Controls:
  - `logs/ablation_runs/phase-coarse-s42/metrics.json`
  - `logs/ablation_runs/phase-coarse-s123/metrics.json`
  - `logs/ablation_runs/phase-coarse-s777/metrics.json`
  - `logs/ablation_runs/phase-analog-s42/metrics.json`
  - `logs/ablation_runs/phase-analog-s123/metrics.json`
  - `logs/ablation_runs/phase-analog-s777/metrics.json`
  - `logs/ablation_runs/phase-nonlinear-s42/metrics.json`
  - `logs/ablation_runs/phase-nonlinear-s123/metrics.json`
  - `logs/ablation_runs/phase-nonlinear-s777/metrics.json`
  - `logs/ablation_runs/phase-insensitive-s42/metrics.json`
  - `logs/ablation_runs/phase-insensitive-s123/metrics.json`
  - `logs/ablation_runs/phase-insensitive-s777/metrics.json`
