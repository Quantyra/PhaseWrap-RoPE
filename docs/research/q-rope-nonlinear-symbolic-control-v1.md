# Nonlinear symbolic control result

## Packet
- Task: `synthetic_dual_nonlinear_manifold_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Candidate: `V_future_relational_witness_nonlinear`
- Control: `V_control_symbolic_nonlinear_manifold_regressor`

## Means
| Variant | Mean MAE | Mean rank correlation | Mean calibration slope |
|---|---:|---:|---:|
| `V_future_relational_witness_nonlinear` | `0.122052` | `0.942097` | `0.860136` |
| `V_control_symbolic_nonlinear_manifold_regressor` | `0.110015` | `0.899455` | `0.975470` |

## Reading
- The bounded nonlinear symbolic control did not collapse the branch into a trivial lookup.
- But it did beat the witness on the primary regression metric, mean MAE.
- The witness kept slightly stronger mean rank correlation, but that is not enough to claim uniqueness on this task.
