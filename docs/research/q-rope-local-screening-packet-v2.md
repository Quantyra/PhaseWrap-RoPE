# Q-RoPE Local Screening Packet v2

## Scope
- Backend: `sim_quantum_statevector`
- Circuit: redesigned local screening circuit with:
  - forward CNOT chain
  - global `RX(pi/4)` mixing layer
  - reverse CNOT chain
  - weighted all-qubit excitation readout
- Variants: `V3`, `V4`, `V4b`
- Datasets: `yelp`, `imdb`, `amazon`
- Seeds: `42`, `123`, `777`
- Credit usage: `0`

## Main outcome
The redesigned local screening gate is now informative.

It no longer collapses `V3`, `V4`, and `V4b` into identical aggregate outcomes.

## Summary

| Dataset | Variant | Mean Acc | Std Acc | Mean F1 | Std F1 | Worst Acc |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `amazon` | `V3` | 0.5833 | 0.1909 | 0.6406 | 0.1702 | 0.3750 |
| `amazon` | `V4` | 0.5833 | 0.1909 | 0.6406 | 0.1702 | 0.3750 |
| `amazon` | `V4b` | 0.5833 | 0.1909 | 0.6053 | 0.1802 | 0.3750 |
| `imdb` | `V3` | 0.4583 | 0.2602 | 0.5315 | 0.1905 | 0.2500 |
| `imdb` | `V4` | 0.4167 | 0.1909 | 0.4720 | 0.0890 | 0.2500 |
| `imdb` | `V4b` | 0.4583 | 0.1909 | 0.5238 | 0.1082 | 0.2500 |
| `yelp` | `V3` | 0.4583 | 0.0722 | 0.2593 | 0.2313 | 0.3750 |
| `yelp` | `V4` | 0.5000 | 0.0000 | 0.2778 | 0.2546 | 0.5000 |
| `yelp` | `V4b` | 0.5000 | 0.1250 | 0.3016 | 0.2870 | 0.3750 |

## Interpretation
The redesigned local gate now separates variants, but the picture is mixed.

### `amazon`
- no accuracy separation
- `V4b` is slightly worse on F1

### `imdb`
- `V4` and `V4b` reduce accuracy variance vs `V3`
- `V4b` preserves mean accuracy relative to `V3`
- `V4` regresses mean accuracy

### `yelp`
- `V4` improves mean accuracy and reduces variance
- `V4b` improves mean accuracy but increases variance vs `V3`

## Decision
- Decision: `NO-GO` for a paid remote `V4b` wave right now

Reason:
- `V4b` does not clearly dominate `V3`
- `V4b` does not clearly beat damped-only `V4`
- improvement is dataset-dependent and not strong enough yet to justify remote budget

## What improved
- the local gate is now technically meaningful
- we can use it to screen future variants without the previous observability failure

## What remains unresolved
- whether a better `V4b`-class variant exists
- whether `V4` or `V4b` should be the active stability track
- whether larger-sample local packets would smooth the current dataset-specific behavior

## Bottom line
The local screening infrastructure is now usable.
The current `V4b` result is informative, but not strong enough to justify remote promotion.
