# First phase-sensitive manifold packet

## Packet
- Task: `synthetic_dual_phase_sensitive_manifold_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Candidate: `V_future_relational_witness_phase_sensitive`
- Controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_nonlinear_manifold_regressor`
  - `V_control_symbolic_phase_insensitive_regressor`

## Means
| Variant | Mean MAE | Mean rank correlation | Mean calibration slope |
|---|---:|---:|---:|
| `V_future_relational_witness_phase_sensitive` | `0.482448` | `0.905306` | `0.875856` |
| `V_control_symbolic_coarse_lookup_regressor` | `0.288657` | `0.054453` | `0.690362` |
| `V_control_symbolic_analog_only_regressor` | `0.295953` | `0.025394` | `-0.220875` |
| `V_control_symbolic_nonlinear_manifold_regressor` | `0.201769` | `0.931780` | `1.009754` |
| `V_control_symbolic_phase_insensitive_regressor` | `0.368213` | `0.946864` | `1.147382` |

## Reading
- The witness did not survive the fixed control stack.
- Both nonlinear controls beat the witness on mean MAE.
- The previously successful nonlinear manifold control remained the strongest baseline overall.
- The new phase-insensitive control also beat the witness on the primary metric, so state-conditioned phase structure did not rescue the branch.
