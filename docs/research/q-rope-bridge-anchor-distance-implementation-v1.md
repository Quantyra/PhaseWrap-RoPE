# Q-RoPE Bridge Anchor-Distance Implementation v1

## Scope
- Task: `synthetic_positional_anchor_distance_response`
- Witness: `V_future_relational_witness_positional_anchor_distance`
- Control: `V_control_symbolic_positional_anchor_distance_regressor`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`

## Implementation
- Added the anchor-distance bridge-task synthetic generator to `src/qrope/synthetic.py`.
- Added witness/control feature extraction and dispatch in `src/qrope/run.py`.
- Added focused tests for generator diagnostics and both model paths.

## Validation
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- Result: `312 passed`

## Artifact
- Summary CSV: `logs/ablation_runs/summary/bridge_anchor_distance_v1.csv`
