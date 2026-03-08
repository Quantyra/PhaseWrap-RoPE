# Q-RoPE First V_new Synthetic Packet v1

## Scope
- Story: `S108`
- Packet: `V0` vs `V_new_explicit_interference`
- Dataset: `synthetic_offset_binary`
- Seeds: `42`, `123`, `777`
- Backend: `sim_quantum_statevector`
- Readout: `parity`

## Per-seed results
| Variant | Seed | Accuracy | F1 | Positive-minus-negative offset gap | Overall score mean |
| --- | --- | ---: | ---: | ---: | ---: |
| `V0` | `42` | `0.562500` | `0.481481` | `0.017148` | `0.498698` |
| `V0` | `123` | `0.554688` | `0.521008` | `0.012244` | `0.504131` |
| `V0` | `777` | `0.492188` | `0.380952` | `0.025629` | `0.503633` |
| `V_new_explicit_interference` | `42` | `0.492188` | `0.545455` | `-0.011029` | `0.457883` |
| `V_new_explicit_interference` | `123` | `0.531250` | `0.491525` | `0.006567` | `0.470310` |
| `V_new_explicit_interference` | `777` | `0.507812` | `0.388350` | `-0.000748` | `0.484171` |

## Packet means
| Variant | Mean accuracy | Mean F1 | Mean positive-minus-negative offset gap | Mean score |
| --- | ---: | ---: | ---: | ---: |
| `V0` | `0.536459` | `0.461147` | `0.018340` | `0.502154` |
| `V_new_explicit_interference` | `0.510417` | `0.475110` | `-0.001737` | `0.470788` |

## Result
- `NO-GO` on the fixed falsification packet

## Why it failed
- The packet is mixed on metrics:
  - `V_new_explicit_interference` improves mean `F1`
  - `V0` retains better mean `accuracy`
- More importantly, `V_new_explicit_interference` fails the core mechanism gate:
  - it does not improve signed offset separation over `V0`
  - its mean positive-minus-negative offset gap is lower and flips negative overall

## Interpretation
- The new comparator is executable.
- It does not currently produce the intended relative-offset advantage.
- This is not just another uniform score-shift failure:
  - the mean score also drops versus `V0`
  - but the offset-sensitive separation target still does not improve
- The correct next step is a decision memo, not broader execution.

## Artifacts
- `logs/ablation_runs/v0-synthetic-s42/`
- `logs/ablation_runs/v0-synthetic-s123/`
- `logs/ablation_runs/v0-synthetic-s777/`
- `logs/ablation_runs/vnew-synthetic-s42/`
- `logs/ablation_runs/vnew-synthetic-s123/`
- `logs/ablation_runs/vnew-synthetic-s777/`

