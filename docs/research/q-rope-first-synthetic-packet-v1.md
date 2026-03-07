# Q-RoPE First Synthetic Packet v1

## Packet
- dataset: `synthetic_offset_binary`
- backend: `sim_quantum_statevector`
- readout: `parity`
- variants:
  - `V0`
  - `V3`
- seeds:
  - `42`
  - `123`
  - `777`

## Results
| Variant | Seed | Accuracy | F1 |
|---|---:|---:|---:|
| `V0` | `42` | `0.562500` | `0.481481` |
| `V0` | `123` | `0.554688` | `0.521008` |
| `V0` | `777` | `0.492188` | `0.380952` |
| `V3` | `42` | `0.507812` | `0.350515` |
| `V3` | `123` | `0.484375` | `0.571429` |
| `V3` | `777` | `0.562500` | `0.645570` |

## Means
- `V0`
  - mean accuracy: `0.536459`
  - mean F1: `0.461147`
- `V3`
  - mean accuracy: `0.518229`
  - mean F1: `0.522505`

## Decision
- `NO-GO` for claiming a positive synthetic salvage signal
- current state: `null-to-inconclusive`

## Why this is not a positive salvage result
The restart gate required `V3` to beat `V0` on a synthetic family in a way that is consistent across seeds and mechanistically interpretable.

That did not happen here.

Observed pattern:
- `V0` is better on accuracy in seeds `42` and `123`
- `V3` is better on accuracy only in seed `777`
- `V3` has higher mean F1, but that gain is not matched by mean accuracy
- the metric split suggests unstable thresholding or class-decision geometry rather than a clean relative-offset mechanism win

## Interpretation
This packet does not support the claim that the current `V3` implementation expresses a clearly stronger signed relative-offset inductive bias than `V0`.

At best, it suggests:
- some response differences exist
- but they are not stable enough or clean enough to count as a synthetic rescue of the program

## Practical implication
The synthetic salvage path is materially weakened.

It is not fully dead yet, but the burden is now much higher:
- any continuation would need score-vs-offset diagnostics that show a real mechanism advantage for `V3`
- without that, further restart effort is not justified

## Next step
Run one diagnostic-only follow-up:
- compare score-vs-offset curves for `V0` and `V3`
- if those curves do not show a clearer relative-offset structure under `V3`, pause the salvage path
