# First nonlinear manifold packet

## Packet
- Task: `synthetic_dual_nonlinear_manifold_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Candidate: `V_future_relational_witness_nonlinear`
- Controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_full_declared_additive_regressor`

## Means
| Variant | Mean MAE | Mean rank correlation | Mean calibration slope |
|---|---:|---:|---:|
| `V_future_relational_witness_nonlinear` | `0.122052` | `0.942097` | `0.860136` |
| `V_control_symbolic_coarse_lookup_regressor` | `0.255825` | `0.127133` | `-0.290818` |
| `V_control_symbolic_analog_only_regressor` | `0.264195` | `0.244688` | `0.461095` |
| `V_control_symbolic_full_declared_additive_regressor` | `0.257792` | `0.279627` | `0.503675` |

## Reading
- The candidate beat all approved additive controls on all three seeds.
- The task centering did suppress the coarse lookup shortcut as intended.
- The additive analog controls remained materially weaker than the witness path.
- This is the first continuous branch in the repo where the witness line cleanly survived the approved additive control stack.
