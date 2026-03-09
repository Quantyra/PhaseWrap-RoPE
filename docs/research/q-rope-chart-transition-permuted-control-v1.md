# Chart-transition permuted control result

## Packet
- task: `synthetic_dual_chart_transition_manifold_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- compared witness against the bounded permuted-transition control only

## Mean results
- `V_future_relational_witness_chart_transition`
  - MAE: `0.140193`
  - rank correlation: `0.915337`
  - calibration slope: `0.990147`
- `V_control_symbolic_transition_permuted_regressor`
  - MAE: `0.189508`
  - rank correlation: `0.736893`
  - calibration slope: `0.897505`

## Interpretation
- the permuted ordered-transition control did not match the witness
- the chart-transition task still appears to require more than one favorable ordered transition table
- the branch remains active
