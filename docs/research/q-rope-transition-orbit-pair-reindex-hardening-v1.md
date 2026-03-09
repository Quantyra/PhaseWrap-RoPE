# Transition Orbit Pair-Reindex Hardening v1

## Mean results
| Variant | Mean MAE | Mean Rank Correlation | Mean Calibration Slope |
| --- | ---: | ---: | ---: |
| `V_future_relational_witness_transition_orbit` | `0.087772` | `0.911945` | `1.022924` |
| `V_control_symbolic_transition_orbit_additive_regressor` | `0.120840` | `0.877528` | `1.048022` |
| `V_control_symbolic_transition_additive_regressor` | `0.120840` | `0.877528` | `1.048022` |
| `V_control_symbolic_transition_cross_direction_regressor` | `0.122814` | `0.874567` | `1.033374` |
| `V_control_symbolic_transition_quadratic_regressor` | `0.126617` | `0.881461` | `1.023609` |
| `V_control_symbolic_transition_unordered_regressor` | `0.170763` | `0.692610` | `0.804220` |

## Readout
- The witness remained strongest on mean MAE.
- The witness also remained strongest on mean rank correlation.
- `pair_reindex = 1` did not collapse the branch.
