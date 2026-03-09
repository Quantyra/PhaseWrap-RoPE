# First orthogonalized continuous packet

## Packet
- Task: `synthetic_dual_orthogonalized_continuous_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Candidate: `V_future_relational_witness_orthogonalized`
- Controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_full_declared_residual_regressor`

## Means
| Variant | Mean MAE | Mean rank correlation | Mean calibration slope |
|---|---:|---:|---:|
| `V_future_relational_witness_orthogonalized` | `0.093584` | `0.923990` | `0.943096` |
| `V_control_symbolic_coarse_lookup_regressor` | `0.180238` | `-0.018376` | `-342.951211` |
| `V_control_symbolic_analog_only_regressor` | `0.066729` | `0.962434` | `1.014410` |
| `V_control_symbolic_full_declared_residual_regressor` | `0.069405` | `0.946335` | `0.998567` |

## Reading
- Orthogonalization worked against the coarse lookup baseline.
- The candidate beat the coarse lookup control cleanly.
- The candidate did not beat the analog-only or full declared residual controls.
- So the branch improved task fairness, but it did not produce a uniqueness win for the witness path.
