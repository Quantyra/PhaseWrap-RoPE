# Chart-transition bidirectional control result

## Packet
- task: `synthetic_dual_chart_transition_manifold_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- compared witness against the bounded bidirectional-transition control only

## Mean results
- `V_future_relational_witness_chart_transition`
  - MAE: `0.140193`
  - rank correlation: `0.915337`
  - calibration slope: `0.990147`
- `V_control_symbolic_transition_bidirectional_regressor`
  - MAE: `0.149888`
  - rank correlation: `0.836061`
  - calibration slope: `1.034456`

## Interpretation
- the bidirectional ordered-transition control still did not match the witness
- the chart-transition task now appears to require more than separate access to forward and reversed transition families in one bounded linear control
- the branch remains active
