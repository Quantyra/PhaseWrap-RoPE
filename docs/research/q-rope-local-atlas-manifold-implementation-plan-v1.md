# Local atlas manifold implementation plan

## Task
- `synthetic_dual_local_atlas_manifold_response`

## Candidate
- `V_future_relational_witness_local_atlas`

## Fixed controls
- `V_control_symbolic_coarse_lookup_regressor`
- `V_control_symbolic_analog_only_regressor`
- `V_control_symbolic_nonlinear_manifold_regressor`
- `V_control_symbolic_phase_insensitive_regressor`
- `V_control_symbolic_global_phase_regressor`
- `V_control_symbolic_single_chart_regressor`

## Writable scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Required diagnostics
- coarse tuple mean absolute max
- within-state variation flag
- candidate/control mean MAE
- candidate/control rank correlation
- candidate/control calibration slope
- proof that chart ids are absent from all controls
- proof that the single-chart control uses one global residual map only

## Fixed first packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- task only
- candidate plus six fixed controls only

## Stop rule
Stop immediately after the first packet unless the candidate beats every fixed control on the primary regression metric while preserving strong rank ordering.
