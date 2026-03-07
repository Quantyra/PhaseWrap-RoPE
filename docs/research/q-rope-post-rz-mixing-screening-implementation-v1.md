# Q-RoPE Post-RZ Mixing Screening Implementation v1

## Scope
This step implemented and screened three fixed local post-`RZ` mixing presets on the primary `V3` path only.

Screened path:
- backend: `sim_quantum_statevector`
- readout: `parity`
- presets:
  - `mix_v0`
  - `mix_v1`
  - `mix_v2`
- datasets:
  - `yelp`
  - `imdb`
  - `amazon`
- seeds:
  - `42`
  - `123`
  - `777`
  - `2024`
  - `9001`

Weighted shadow:
- triggered only for `mix_v2`
- compared `mix_v0` vs `mix_v2`

## Implementation
Updated local-only screening infrastructure:
- `src/qrope/qsim.py`
- `src/qrope/run.py`
- `tests/test_qsim.py`
- `tests/test_run_real_mode.py`

No remote backend behavior changed.

## Parity screen summary
Source:
- `logs/ablation_runs/summary/mixscreen_v1.csv`

### `yelp`
- `mix_v0`: acc `0.600`, std `0.122`; F1 `0.567`, std `0.131`
- `mix_v1`: acc `0.600`, std `0.094`; F1 `0.544`, std `0.157`
- `mix_v2`: acc `0.575`, std `0.061`; F1 `0.627`, std `0.061`

Read:
- `mix_v2` improved F1 and stability.
- `mix_v1` was only a variance reduction without a stronger outcome.

### `imdb`
- `mix_v0`: acc `0.475`, std `0.146`; F1 `0.463`, std `0.065`
- `mix_v1`: acc `0.500`, std `0.079`; F1 `0.542`, std `0.065`
- `mix_v2`: acc `0.475`, std `0.255`; F1 `0.343`, std `0.333`

Read:
- `mix_v1` helped.
- `mix_v2` was unstable and materially worse.

### `amazon`
- `mix_v0`: acc `0.475`, std `0.146`; F1 `0.383`, std `0.205`
- `mix_v1`: acc `0.475`, std `0.166`; F1 `0.322`, std `0.276`
- `mix_v2`: acc `0.550`, std `0.100`; F1 `0.456`, std `0.248`

Read:
- `mix_v2` improved mean accuracy and worst-seed accuracy.
- `mix_v1` regressed.

## Weighted shadow for `mix_v2`
Source:
- `logs/ablation_runs/summary/mixshadow_weighted_v1.csv`

### `yelp`
- `mix_v0`: acc `0.625`; F1 `0.447`
- `mix_v2`: acc `0.525`; F1 `0.339`

### `imdb`
- `mix_v0`: acc `0.525`; F1 `0.372`
- `mix_v2`: acc `0.525`; F1 `0.526`

### `amazon`
- `mix_v0`: acc `0.550`; F1 `0.654`
- `mix_v2`: acc `0.500`; F1 `0.503`

Read:
- `mix_v2` only helped `imdb`.
- `mix_v2` regressed `yelp` and `amazon` under the shadow readout.

## Decision
Decision: `HOLD`

Interpretation:
- `mix_v1` is too narrow. It only helps `imdb`.
- `mix_v2` is the only preset with a credible parity-path case, but the weighted shadow shows the gain is not robust enough to change branch direction.
- No preset currently justifies:
  - a new branch
  - remote budget
  - replacement of the current `V3` primary path

## Protocol consequence
The post-`RZ` mixing screen answered the mechanism question narrowly:
- modest fixed mixing changes can move the local signal
- but they do not yet produce a stable enough gain to promote a new path

The next step should stay zero-credit and local.
The most defensible follow-on is a tighter local mechanism-selection memo before any deeper circuit redesign.
