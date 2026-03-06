# Q-RoPE Local Observable Screening Implementation v1

## Scope
This step implemented configurable local readout selection and executed the zero-credit screening packet for:
- `weighted`
- `q2`
- `parity`

Backend:
- `sim_quantum_statevector`

Credit status:
- `0` additional Quandela credits consumed

## Implementation
Updated:
- `src/qrope/qsim.py`
- `src/qrope/run.py`
- `tests/test_qsim.py`
- `tests/test_run_real_mode.py`

What changed:
- local readout selection is now configurable for the statevector screening path
- default behavior remains `weighted`
- screening candidates `q2` and `parity` can now be run through the same local evaluation path
- remote backends were not changed

## Validation
- focused tests passed: `29 passed`

## Screening packet
Variants:
- `V3`
- `V4`

Datasets:
- `yelp`
- `imdb`
- `amazon`

Seeds:
- `42`
- `123`
- `777`
- `2024`
- `9001`

Readouts:
- `weighted`
- `q2`
- `parity`

Run IDs:
- `obs-weighted-*`
- `obs-q2-*`
- `obs-parity-*`

## Result
### Yelp
`V3`
- `weighted`: mean acc `0.6250`, std `0.1118`, mean F1 `0.4467`
- `q2`: mean acc `0.5750`, std `0.0612`, mean F1 `0.4476`
- `parity`: mean acc `0.6000`, std `0.1225`, mean F1 `0.5665`

`V4`
- `weighted`: mean acc `0.5750`, std `0.1000`, mean F1 `0.3976`
- `q2`: mean acc `0.5000`, std `0.0791`, mean F1 `0.3558`
- `parity`: mean acc `0.5500`, std `0.1275`, mean F1 `0.4922`

### IMDb
`V3`
- `weighted`: mean acc `0.5250`, std `0.2151`, mean F1 `0.3721`
- `q2`: mean acc `0.4500`, std `0.1000`, mean F1 `0.3033`
- `parity`: mean acc `0.4750`, std `0.1458`, mean F1 `0.4632`

`V4`
- `weighted`: mean acc `0.5250`, std `0.2151`, mean F1 `0.3721`
- `q2`: mean acc `0.4750`, std `0.0935`, mean F1 `0.3226`
- `parity`: mean acc `0.5000`, std `0.1118`, mean F1 `0.4982`

### Amazon
`V3`
- `weighted`: mean acc `0.5500`, std `0.1696`, mean F1 `0.6542`
- `q2`: mean acc `0.4500`, std `0.1000`, mean F1 `0.3662`
- `parity`: mean acc `0.4750`, std `0.1458`, mean F1 `0.3834`

`V4`
- `weighted`: mean acc `0.5000`, std `0.1581`, mean F1 `0.5600`
- `q2`: mean acc `0.4750`, std `0.0935`, mean F1 `0.4329`
- `parity`: mean acc `0.5500`, std `0.1871`, mean F1 `0.5733`

## Interpretation
`q2` is not good enough.

It reduces variance, but the mean-performance drop is too large across all datasets.

`parity` is the only viable screening-path upgrade candidate:
- on `yelp`, it materially improves F1
- on `imdb`, it improves F1 and reduces variance relative to weighted
- on `amazon`, it remains weaker for `V3`, but becomes competitive or slightly better for `V4`

This is still not an algorithm result.
It is a local screening-path result.

## Decision
- `q2`: `NO-GO`
- `parity`: `GO` for further local screening-path evaluation

## Bottom line
The local observable upgrade question produced one viable candidate: `parity`.
The next step should evaluate whether parity is strong enough to become the default local screening readout.
