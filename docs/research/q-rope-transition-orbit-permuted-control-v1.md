# Transition Orbit Permuted Control v1

## Packet
- fixed six-run packet
- dataset: `synthetic_chart_transition_orbit_response`
- seeds: `42`, `123`, `777`
- witness: `V_future_relational_witness_transition_orbit`
- control: `V_control_symbolic_transition_orbit_permuted_regressor`

## Means
- witness
  - MAE `0.089852`
  - rank correlation `0.847172`
  - calibration slope `1.139148`
- permuted control
  - MAE `0.170728`
  - rank correlation `0.517480`
  - calibration slope `0.940185`

## Interpretation
- the orbit-canonical permuted control remained materially weaker than the witness on both primary metrics
- the branch is not explained by one favorable transition-table assignment under orbit-canonical rendering
