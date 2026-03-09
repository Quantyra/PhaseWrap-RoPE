# Chart-transition cubic control result

## Packet
- task: `synthetic_dual_chart_transition_manifold_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- compared witness against the bounded cubic transition-family control only

## Mean results
- `V_future_relational_witness_chart_transition`
  - MAE: `0.140193`
  - rank correlation: `0.915337`
  - calibration slope: `0.990147`
- `V_control_symbolic_transition_cubic_regressor`
  - MAE: `0.157829`
  - rank correlation: `0.836061`
  - calibration slope: `1.042150`

## Interpretation
- the fixed cubic transition-family control still did not match the witness
- bounded symbolic basis expansion is no longer closing the gap on this task
- the branch remains active and should move to hardening rather than larger symbolic families
