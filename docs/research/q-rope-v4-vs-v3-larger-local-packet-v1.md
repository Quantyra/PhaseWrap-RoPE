# Q-RoPE V4 vs V3 Larger Local Packet v1

## Scope
- Backend: `sim_quantum_statevector`
- Circuit: redesigned local screening circuit
- Variants: `V3`, `V4`
- Datasets: `yelp`, `imdb`, `amazon`
- Seeds: `42`, `123`, `777`, `2024`, `9001`
- Credit usage: `0`

## Summary

| Dataset | Variant | Mean Acc | Std Acc | Mean F1 | Std F1 | Worst Acc |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `amazon` | `V3` | 0.4750 | 0.2054 | 0.5532 | 0.1704 | 0.2500 |
| `amazon` | `V4` | 0.5000 | 0.1768 | 0.5621 | 0.1613 | 0.3750 |
| `imdb` | `V3` | 0.5250 | 0.2054 | 0.5665 | 0.1469 | 0.2500 |
| `imdb` | `V4` | 0.4500 | 0.1677 | 0.4546 | 0.1214 | 0.2500 |
| `yelp` | `V3` | 0.5750 | 0.1677 | 0.4556 | 0.3146 | 0.3750 |
| `yelp` | `V4` | 0.6000 | 0.1369 | 0.4667 | 0.3151 | 0.5000 |

## Interpretation
`V4` remains defensible as the active local stability track, but the larger packet still does not justify a new remote wave.

### `amazon`
- `V4` improves mean accuracy slightly
- `V4` reduces variance slightly
- `V4` improves worst-seed accuracy

### `yelp`
- `V4` improves mean accuracy slightly
- `V4` reduces variance slightly
- `V4` improves worst-seed accuracy

### `imdb`
- `V4` reduces variance
- but regresses materially in mean accuracy and mean F1
- worst-seed accuracy does not improve

## Decision
- Decision: `HOLD` on new remote `V4` execution

## Why this is the correct decision
The larger local packet did not collapse `V4`.
But it also did not create a strong enough, cross-dataset-stable signal to justify new remote spend.

The current local evidence says:
- `V4` is still the best local stability-oriented branch to keep exploring
- `V4` is not yet strong enough to support a new remote wave as a decision-grade priority

## Recommended next step
Stay local and zero-credit.

Best next move:
- run one more local refinement wave that targets the `imdb` regression specifically
- do not reopen `V4b`
- do not spend Quandela credits yet

## Bottom line
`V4` survives the modest local scale-up.
It does not yet earn a new remote question.
