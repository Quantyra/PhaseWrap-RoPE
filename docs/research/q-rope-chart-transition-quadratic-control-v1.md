# Chart-transition quadratic control result

## Packet
- task: `synthetic_dual_chart_transition_manifold_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- compared witness against the bounded quadratic transition-family control only

## Mean results
- `V_future_relational_witness_chart_transition`
  - MAE: `0.140193`
  - rank correlation: `0.915337`
  - calibration slope: `0.990147`
- `V_control_symbolic_transition_quadratic_regressor`
  - MAE: `0.157925`
  - rank correlation: `0.836061`
  - calibration slope: `1.040828`

## Interpretation
- the fixed quadratic transition-family control did not match the witness
- the chart-transition task now appears to require more than a bounded second-order basis over the declared transition-family features
- the branch remains active
