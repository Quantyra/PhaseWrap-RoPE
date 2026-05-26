# `qrope.scoring` API

Status: stable public review API.

Package API version: `0.1.0`. Evidence release version: `0.3.1-negative-results`.

These versions are intentionally separate: the Python package API tracks import/runtime compatibility, while the evidence release tracks the frozen publication packet archived through GitHub/Zenodo.

The scoring API exposes the compact PhaseWrap primitive without hardware-provider dependencies. It is the preferred entry point for reviewers who want to inspect or reuse the mathematical scoring rule directly.

```python
from qrope import phase_margins, phase_residual, phasewrap_features, phasewrap_score

score = phasewrap_score(reference_delta=37, candidate_delta=13)
features = phasewrap_features(reference_delta=37, candidate_delta=13)
```

## Functions

### `phase_residual(reference_delta, candidate_delta, period)`

Returns the absolute wrapped phase residual between two integer deltas for one period. The residual is measured in radians after wrapping to `[-pi, pi]`.

The implementation uses constant-time modular wrapping via `math.remainder`; it does not repeatedly add or subtract `2*pi` for large offsets.

### `phase_margins(reference_delta, candidate_delta, period_pair=(8, 12))`

Returns the two signed margins used by the fixed score:

```text
m_p = cos(residual_p) - cos(2*pi/p)
```

The returned dictionary always includes:

- `first_period`, `second_period`
- `first_margin`, `second_margin`
- `first_residual`, `second_residual`
- `margins_by_period`
- `residuals_by_period`

For the default `(8, 12)` pair only, the dictionary also includes compatibility aliases `m8` and `m12`.

For custom period pairs, use `first_margin`/`second_margin` or the period-keyed dictionaries. The `m8`/`m12` aliases are intentionally omitted for non-default pairs so callers do not accidentally treat the second period as `12`.

### `phasewrap_score(reference_delta, candidate_delta, period_pair=(8, 12))`

Returns the fixed PhaseWrap score:

```text
SQR = m8 * m12
```

This score is exactly computable on a CPU. The hardware lane in this repository is a bounded noisy-readout witness for this classical object, not a claim that the score needs quantum computation.

### `phasewrap_features(reference_delta, candidate_delta, period_pair=(8, 12))`

Returns a JSON-friendly feature dictionary containing the input deltas, period metadata, residuals, margins, and score.

## Install Paths

Core API only:

```bash
python -m pip install -e .
```

Reviewer verification path:

```bash
python -m pip install -r requirements-review.txt
python -m pip install -e .
```

Provider stacks are optional and intentionally separated:

```bash
python -m pip install -e ".[ibm]"
python -m pip install -e ".[braket]"
python -m pip install -e ".[hardware]"
```
