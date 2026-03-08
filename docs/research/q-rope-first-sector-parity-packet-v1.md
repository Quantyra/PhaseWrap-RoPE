# Q-RoPE First Sector-Parity Packet v1

## Scope
- Story: `S147`
- Dataset: `synthetic_sector_parity_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Variants:
  - `V0`
  - `V_future_sector_contrast_pairstate`

## Per-seed results
| Variant | Seed | Accuracy | F1 | Positive-minus-negative offset gap | Task contrast mean | Anti-collapse |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `V0` | `42` | `0.578125` | `0.550000` | `0.012141` | `n/a` | `n/a` |
| `V0` | `123` | `0.484375` | `0.459016` | `-0.008345` | `n/a` | `n/a` |
| `V0` | `777` | `0.500000` | `0.418182` | `0.001798` | `n/a` | `n/a` |
| `V_future_sector_contrast_pairstate` | `42` | `0.500000` | `0.666667` | `-0.018141` | `-0.006262` | `true` |
| `V_future_sector_contrast_pairstate` | `123` | `0.500000` | `0.666667` | `-0.018229` | `-0.004593` | `true` |
| `V_future_sector_contrast_pairstate` | `777` | `0.500000` | `0.666667` | `-0.017798` | `-0.005731` | `true` |

## Packet means
| Variant | Mean accuracy | Mean F1 | Mean offset gap | Mean task contrast |
| --- | ---: | ---: | ---: | ---: |
| `V0` | `0.520833` | `0.475733` | `0.001865` | `n/a` |
| `V_future_sector_contrast_pairstate` | `0.500000` | `0.666667` | `-0.018056` | `-0.005529` |

## Decision
- `NO-GO`

## Why it failed
The candidate did not satisfy the approved restart gate.

It failed on the task’s key standard:
- it did not beat `V0` on mean accuracy
- its task-relevant contrast was negative on all three seeds

The candidate did preserve:
- sector resolution before aggregation
- anti-collapse pass

So the mechanism stayed structurally disciplined.
But the alignment-safe task removed the apparent advantage.

## Correct interpretation
This is a clean falsification result for the bounded restart:
- the earlier pair-state promise does not survive the alignment-safe sector-parity task in its first approved form

## Bottom line
- useful restart test
- negative result
- do not broaden
