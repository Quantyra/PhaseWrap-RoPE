# Transition Orbit First Packet v1

## Mean results
| Variant | Mean MAE | Mean Rank Correlation | Mean Calibration Slope |
| --- | ---: | ---: | ---: |
| `V_future_relational_witness_transition_orbit` | `0.089852` | `0.847172` | `0.981829` |
| `V_control_symbolic_transition_cross_direction_regressor` | `0.109929` | `0.771406` | `0.980641` |
| `V_control_symbolic_transition_orbit_additive_regressor` | `0.111178` | `0.767470` | `0.985415` |
| `V_control_symbolic_transition_additive_regressor` | `0.111178` | `0.767470` | `0.985415` |
| `V_control_symbolic_transition_quadratic_regressor` | `0.111733` | `0.775342` | `0.970523` |
| `V_control_symbolic_transition_unordered_regressor` | `0.150015` | `0.560999` | `0.785535` |

## Readout
- The witness beat every approved control on mean MAE.
- The witness also led on mean rank correlation.
- The orbit gate passed before packet interpretation.

## Artifact
- `logs/ablation_runs/summary/transition_orbit_v1.csv`
