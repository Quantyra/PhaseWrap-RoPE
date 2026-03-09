# Token-Invariant Chart-Transition First Packet v1

## Packet
- Dataset: `synthetic_chart_transition_token_invariant_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Candidate:
  - `V_future_relational_witness_chart_transition_invariant`
- Controls:
  - `V_control_symbolic_transition_additive_regressor`
  - `V_control_symbolic_transition_unordered_regressor`
  - `V_control_symbolic_transition_cross_direction_regressor`
  - `V_control_symbolic_transition_quadratic_regressor`

## Mean results
| Variant | Mean MAE | Mean Rank Correlation | Mean Calibration Slope |
| --- | ---: | ---: | ---: |
| `V_control_symbolic_transition_additive_regressor` | `0.277886` | `0.225557` | `0.171691` |
| `V_control_symbolic_transition_quadratic_regressor` | `0.278620` | `0.122923` | `0.024119` |
| `V_control_symbolic_transition_cross_direction_regressor` | `0.280120` | `0.243014` | `0.138530` |
| `V_control_symbolic_transition_unordered_regressor` | `0.284955` | `0.061110` | `-0.063669` |
| `V_future_relational_witness_chart_transition_invariant` | `0.310960` | `0.081770` | `0.167864` |

## Readout
- The invariance gate passed before packet interpretation.
- The witness lost to all approved controls on mean MAE.
- The witness also failed to lead on mean rank correlation.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/chart_transition_token_invariant_v1.csv`
