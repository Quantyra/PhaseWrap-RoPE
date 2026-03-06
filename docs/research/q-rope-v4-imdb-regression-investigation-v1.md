# Q-RoPE V4 IMDb Regression Investigation v1

## Scope
Investigated the `imdb` regression from the five-seed local `V4` vs `V3` packet using the current redesigned local screening circuit.

## Finding
The `imdb` regression does not look like random packet noise.
It looks like a threshold-calibration problem combined with weaker class separation on the affected seeds.

## Evidence
Across `imdb` seeds:
- `V4` consistently raises the train-calibrated threshold relative to `V3`
- on the weaker seeds, the positive-vs-negative score margin is small enough that the higher threshold hurts classification

Representative results:

| Seed | Variant | Threshold | Pos Mean | Neg Mean | Margin | Accuracy | F1 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `123` | `V3` | 0.4365 | 0.4726 | 0.4002 | 0.0724 | 0.7500 | 0.7500 |
| `123` | `V4` | 0.4634 | 0.4894 | 0.4257 | 0.0638 | 0.6250 | 0.5714 |
| `2024` | `V3` | 0.4468 | 0.4221 | 0.4073 | 0.0148 | 0.6250 | 0.6667 |
| `2024` | `V4` | 0.4679 | 0.4466 | 0.4306 | 0.0160 | 0.3750 | 0.2857 |

Additional signal:
- predicted positive rate drops on the problematic seeds:
  - seed `123`: `V3=0.500`, `V4=0.375`
  - seed `2024`: `V3=0.625`, `V4=0.375`

## Interpretation
`V4` is not uniformly worse on `imdb`.
It appears to be more sensitive to the current train-mean threshold rule on seeds where the class-separation margin is already small.

So the current `imdb` issue is more specifically:
- `V4` plus current threshold calibration
rather than simply:
- `V4` is structurally broken on `imdb`

## Decision impact
`V4` remains the active local track.

Why:
- the regression appears tied to calibration behavior, not a clear collapse of the underlying scoring signal
- `amazon` and `yelp` still support `V4`
- the next best zero-credit step is calibration-focused, not a new variant branch and not remote execution

## Recommended next step
Run a local calibration investigation for `V4` on `imdb`:
- compare current train-mean threshold against:
  - median threshold
  - class-balanced threshold search on train
  - validation-split threshold selection

Goal:
- determine whether the `imdb` regression survives after a more robust local decision rule

## Bottom line
The `imdb` regression is real, but it currently looks calibration-linked rather than purely structural.
