# Q-RoPE Pair-State Sector-Permutation Control v1

## Scope
- Story: `S133`
- Variant: `V_pairstate_relational`
- Dataset: `synthetic_offset_binary`
- Seeds: `42`, `123`, `777`
- Backend: `sim_quantum_statevector`
- Modes compared:
  - `aligned`
  - `sector_permuted`

## Per-seed results
| Run | Control | Accuracy | F1 | Positive-minus-negative offset gap | Signed contrast mean | Magnitude balance mean |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `pairstate-aligned-s42` | `aligned` | `1.000000` | `1.000000` | `0.241001` | `-0.000556` | `0.200998` |
| `pairstate-aligned-s123` | `aligned` | `1.000000` | `1.000000` | `0.175881` | `0.035607` | `0.136072` |
| `pairstate-aligned-s777` | `aligned` | `1.000000` | `1.000000` | `0.241382` | `-0.000767` | `0.201378` |
| `pairstate-permuted-s42` | `sector_permuted` | `0.750000` | `0.800000` | `0.011277` | `-0.006262` | `0.200998` |
| `pairstate-permuted-s123` | `sector_permuted` | `0.750000` | `0.800000` | `0.008270` | `-0.004593` | `0.136072` |
| `pairstate-permuted-s777` | `sector_permuted` | `0.750000` | `0.800000` | `0.010321` | `-0.005731` | `0.201378` |

## Mean comparison
| Control | Mean accuracy | Mean F1 | Mean offset gap | Mean signed contrast | Mean magnitude balance |
| --- | ---: | ---: | ---: | ---: | ---: |
| `aligned` | `1.000000` | `1.000000` | `0.219421` | `0.011428` | `0.179483` |
| `sector_permuted` | `0.750000` | `0.800000` | `0.009956` | `-0.005529` | `0.179483` |

## Interpretation
The control materially weakens the pair-state result.

What changed:
- accuracy fell from `1.000000` to `0.750000`
- F1 fell from `1.000000` to `0.800000`
- offset-gap signal collapsed from `0.219421` to `0.009956`

What did not change:
- magnitude-balance stayed effectively unchanged

That pattern matters.
The branch still produces structured sector responses, but its useful signed separation largely disappears once direct sign alignment is broken.

## Decision
- `VALIDITY LIMIT CONFIRMED`
- `DO NOT EXPAND`

## Correct reading
This is not a null result.

It shows:
- the pair-state mechanism is doing something real
- but the current synthetic win depends heavily on the aligned sector-to-label mapping

So the original positive packet should be treated as:
- mechanism-positive in a narrow synthetic sense
- not sufficient for benchmark expansion
- not sufficient for remote reopening

## Next step
Write one post-control decision memo and decide whether:
- the pair-state branch returns to archive posture
- or remains preserved only as a future representation idea with a higher restart bar
