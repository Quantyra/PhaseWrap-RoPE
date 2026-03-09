# Chart-transition unordered control result

## Packet
- task: `synthetic_dual_chart_transition_manifold_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- compared witness against the bounded unordered-transition control only

## Mean results
- `V_future_relational_witness_chart_transition`
  - MAE: `0.140193`
  - rank correlation: `0.915337`
  - calibration slope: `0.990147`
- `V_control_symbolic_transition_unordered_regressor`
  - MAE: `0.166809`
  - rank correlation: `0.739901`
  - calibration slope: `1.042197`

## Interpretation
- the unordered-transition control did not match the witness
- the chart-transition task still appears to require ordered transition structure
- the branch remains active
