# Transition Orbit Token Renaming Hardening v1

## Packet
- dataset: `synthetic_chart_transition_orbit_response`
- perturbation: `token_permutation = cdab`
- seeds: `42`, `123`, `777`
- witness: `V_future_relational_witness_transition_orbit`
- strongest current symbolic baseline: `V_control_symbolic_transition_cross_direction_regressor`

## Means
- witness
  - MAE `0.089852`
  - rank correlation `0.847172`
  - calibration slope `1.139148`
- strongest baseline
  - MAE `0.109929`
  - rank correlation `0.771406`
  - calibration slope `1.076154`

## Interpretation
- the packet exactly matched the base orbit packet means
- generator diagnostics reported `token_permutation = orbit_canonical`
- this perturbation is inert under orbit-canonical rendering and must not be counted as new robustness evidence
