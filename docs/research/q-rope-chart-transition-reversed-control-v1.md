# Chart-transition reversed control result

## Packet
- task: `synthetic_dual_chart_transition_manifold_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- compared witness against the bounded reversed-transition control only

## Mean results
- `V_future_relational_witness_chart_transition`
  - MAE: `0.140193`
  - rank correlation: `0.915337`
  - calibration slope: `0.990147`
- `V_control_symbolic_transition_reversed_regressor`
  - MAE: `0.187447`
  - rank correlation: `0.697792`
  - calibration slope: `0.941222`

## Interpretation
- the reversed ordered-transition control did not match the witness
- the chart-transition task still appears to require more than one directional convention
- the branch remains active
