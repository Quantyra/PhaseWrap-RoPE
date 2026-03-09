# Transition Orbit Deeper Pair-Reindex Hardening v1

## Packet
- dataset: `synthetic_chart_transition_orbit_response`
- perturbation: `pair_reindex = 7`
- seeds: `42`, `123`, `777`
- witness: `V_future_relational_witness_transition_orbit`
- strongest current symbolic baseline: `V_control_symbolic_transition_cross_direction_regressor`

## Means
- witness
  - MAE `0.103347`
  - rank correlation `0.925361`
  - calibration slope `1.105435`
- strongest baseline
  - MAE `0.094035`
  - rank correlation `0.888944`
  - calibration slope `1.131281`

## Interpretation
- the deeper pair-reindex perturbation was non-inert
- the witness kept a stronger mean rank correlation
- but it lost the primary metric, mean MAE
