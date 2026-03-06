# Q-RoPE V4 Local Threshold Calibration Investigation v1

## Scope
Compared alternative local threshold rules for `V4` on the `imdb` five-seed packet.

Rules evaluated:
- train mean
- train median
- balanced-train threshold search
- validation-split threshold selection

## Aggregate results

| Rule | Mean Acc | Std Acc | Mean F1 | Std F1 |
| --- | ---: | ---: | ---: | ---: |
| `train_mean` | 0.4500 | 0.1677 | 0.4546 | 0.1214 |
| `train_median` | 0.5000 | 0.2500 | 0.5181 | 0.2311 |
| `balanced_train` | 0.5500 | 0.0685 | 0.2933 | 0.2891 |
| `validation_split` | 0.5250 | 0.2236 | 0.5644 | 0.3339 |

Reference from the larger packet:
- `V3` on `imdb`: mean accuracy `0.5250`, std accuracy `0.2054`, mean F1 `0.5665`, std F1 `0.1469`

## Interpretation
Calibration matters.

The current train-mean rule is not the best decision rule for `V4` on `imdb`.

But calibration does **not** fully resolve the blocker:
- `train_median` improves mean performance, but variance gets worse
- `balanced_train` improves mean accuracy, but collapses F1
- `validation_split` roughly recovers `V3`-level mean accuracy and F1, but with materially worse variance

## Decision
`V4` remains the active local track.

But:
- calibration alone is not yet a clean fix
- no new remote `V4` execution is justified from this evidence

## What this means
The `imdb` issue is not purely a model-quality problem.
It is partly a decision-rule problem.

However, the candidate calibration fixes are too unstable or too asymmetric to count as a solid resolution.

## Recommended next step
Stay local and zero-credit.

Best next move:
- define a more robust local calibration protocol for `V4`
- prefer a calibration rule that does not trade away F1 or explode variance
- do not spend Quandela credits yet

## Bottom line
Calibration helps explain the `imdb` regression.
It does not yet rescue `V4` enough to change the remote decision.
