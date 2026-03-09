# Chart-transition manifold first packet

## Packet
- task: `synthetic_dual_chart_transition_manifold_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- compared candidate plus seven fixed controls

## Mean results
- `V_future_relational_witness_chart_transition`
  - MAE: `0.140193`
  - rank correlation: `0.915337`
  - calibration slope: `0.990147`
- `V_control_symbolic_coarse_lookup_regressor`
  - MAE: `0.253376`
  - rank correlation: `-0.126971`
  - calibration slope: `3.343575`
- `V_control_symbolic_analog_only_regressor`
  - MAE: `0.262581`
  - rank correlation: `-0.012231`
  - calibration slope: `1.802905`
- `V_control_symbolic_nonlinear_manifold_regressor`
  - MAE: `0.178817`
  - rank correlation: `0.738898`
  - calibration slope: `1.034663`
- `V_control_symbolic_phase_insensitive_regressor`
  - MAE: `0.176264`
  - rank correlation: `0.682078`
  - calibration slope: `0.937658`
- `V_control_symbolic_global_phase_regressor`
  - MAE: `0.238749`
  - rank correlation: `0.515087`
  - calibration slope: `1.614153`
- `V_control_symbolic_single_chart_regressor`
  - MAE: `0.182032`
  - rank correlation: `0.736893`
  - calibration slope: `0.966845`
- `V_control_symbolic_transition_additive_regressor`
  - MAE: `0.144463`
  - rank correlation: `0.827126`
  - calibration slope: `1.018888`

## Interpretation
- the candidate beat every approved control on mean MAE
- the nearest remaining control is the bounded transition-additive symbolic baseline
- the branch therefore remains active and has earned one bounded pressure test rather than immediate task expansion
