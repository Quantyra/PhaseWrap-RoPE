# First state-sensitive continuous packet

## Packet
- Task: `synthetic_dual_state_sensitive_continuous_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Candidate: `V_future_relational_witness_state_sensitive`
- Controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_full_declared_regressor`

## Means
| Variant | Mean MAE | Mean rank correlation | Mean calibration slope |
|---|---:|---:|---:|
| `V_future_relational_witness_state_sensitive` | `0.490224` | `-0.684490` | `-0.639638` |
| `V_control_symbolic_coarse_lookup_regressor` | `0.099413` | `0.931304` | `1.021842` |
| `V_control_symbolic_analog_only_regressor` | `0.250323` | `0.200950` | `0.764697` |
| `V_control_symbolic_full_declared_regressor` | `0.089889` | `0.911938` | `0.995725` |

## Reading
- The candidate failed cleanly.
- The coarse lookup control already outperformed it by a wide margin.
- The full declared symbolic regressor was strongest overall.
- The candidate preserved anti-collapse discipline, but the task remained dominated by symbolic structure the controls could exploit directly.
