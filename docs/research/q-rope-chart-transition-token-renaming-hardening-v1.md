# Chart-transition token-renaming hardening result

## Packet
- task: `synthetic_dual_chart_transition_manifold_response`
- backend: `sim_quantum_statevector`
- token permutation: `cdab`
- seeds: `42`, `123`, `777`
- compared the witness against the strongest current symbolic baseline only

## Mean results
- `V_future_relational_witness_chart_transition`
  - MAE: `0.159628`
  - rank correlation: `0.927371`
  - calibration slope: `0.903880`
- `V_control_symbolic_transition_cross_direction_regressor`
  - MAE: `0.150121`
  - rank correlation: `0.871216`
  - calibration slope: `0.810316`

## Interpretation
- the witness did not retain the primary-metric lead under the fixed token renaming
- the branch kept stronger rank correlation but lost robustness on MAE
- this is a robustness failure for the current task claim
