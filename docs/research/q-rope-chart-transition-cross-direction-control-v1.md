# Chart-transition cross-direction control result

## Packet
- task: `synthetic_dual_chart_transition_manifold_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- compared witness against the bounded cross-direction interaction control only

## Mean results
- `V_future_relational_witness_chart_transition`
  - MAE: `0.140193`
  - rank correlation: `0.915337`
  - calibration slope: `0.990147`
- `V_control_symbolic_transition_cross_direction_regressor`
  - MAE: `0.149843`
  - rank correlation: `0.836061`
  - calibration slope: `1.033830`

## Interpretation
- the cross-direction interaction control still did not match the witness
- the chart-transition task now appears to require more than one bounded family of forward-reversed interaction terms
- the branch remains active
