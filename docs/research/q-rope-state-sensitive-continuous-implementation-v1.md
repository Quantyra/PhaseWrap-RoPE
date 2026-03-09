# State-sensitive continuous implementation

## Scope
- Implemented only the approved state-sensitive continuous branch on `synthetic_dual_state_sensitive_continuous_response`.
- Added one candidate:
  - `V_future_relational_witness_state_sensitive`
- Added three fixed controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_full_declared_regressor`

## Validation
- Focused suite passed:
  - `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
  - result: `120 passed`

## Packet outputs
- Summary: `logs/ablation_runs/summary/state_sensitive_continuous_v1.csv`
- Candidate:
  - `logs/ablation_runs/state-sensitive-witness-s42/metrics.json`
  - `logs/ablation_runs/state-sensitive-witness-s123/metrics.json`
  - `logs/ablation_runs/state-sensitive-witness-s777/metrics.json`
- Controls:
  - `logs/ablation_runs/state-sensitive-coarse-s42/metrics.json`
  - `logs/ablation_runs/state-sensitive-coarse-s123/metrics.json`
  - `logs/ablation_runs/state-sensitive-coarse-s777/metrics.json`
  - `logs/ablation_runs/state-sensitive-analog-s42/metrics.json`
  - `logs/ablation_runs/state-sensitive-analog-s123/metrics.json`
  - `logs/ablation_runs/state-sensitive-analog-s777/metrics.json`
  - `logs/ablation_runs/state-sensitive-full-s42/metrics.json`
  - `logs/ablation_runs/state-sensitive-full-s123/metrics.json`
  - `logs/ablation_runs/state-sensitive-full-s777/metrics.json`
