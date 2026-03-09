# Orthogonalized continuous implementation

## Scope
- Implemented only the approved orthogonalized continuous branch on `synthetic_dual_orthogonalized_continuous_response`.
- Added one candidate:
  - `V_future_relational_witness_orthogonalized`
- Added three fixed controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_full_declared_residual_regressor`

## Validation
- Focused suite passed:
  - `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
  - result: `124 passed`

## Packet outputs
- Summary: `logs/ablation_runs/summary/orthogonalized_continuous_v1.csv`
- Candidate:
  - `logs/ablation_runs/orth-witness-s42/metrics.json`
  - `logs/ablation_runs/orth-witness-s123/metrics.json`
  - `logs/ablation_runs/orth-witness-s777/metrics.json`
- Controls:
  - `logs/ablation_runs/orth-coarse-s42/metrics.json`
  - `logs/ablation_runs/orth-coarse-s123/metrics.json`
  - `logs/ablation_runs/orth-coarse-s777/metrics.json`
  - `logs/ablation_runs/orth-analog-s42/metrics.json`
  - `logs/ablation_runs/orth-analog-s123/metrics.json`
  - `logs/ablation_runs/orth-analog-s777/metrics.json`
  - `logs/ablation_runs/orth-full-s42/metrics.json`
  - `logs/ablation_runs/orth-full-s123/metrics.json`
  - `logs/ablation_runs/orth-full-s777/metrics.json`
