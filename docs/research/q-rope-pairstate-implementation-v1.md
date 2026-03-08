# Q-RoPE Pair-State Implementation v1

## Scope
- Story: `S129`
- Variant: `V_pairstate_relational`
- Boundary:
  - local-only
  - `synthetic_offset_binary` only
  - no remote changes
  - no benchmark expansion

## What was implemented
- Added `V_pairstate_relational` to the local simulator path in `src/qrope/qsim.py`
- Added ordered token-pair compositional content encoding
- Added four-sector relative-offset handling:
  - `P_small`
  - `P_large`
  - `N_small`
  - `N_large`
- Added sector-resolved signed-response scoring
- Added sector-first diagnostics in `src/qrope/run.py`

## Validation
- Focused local suite passed:
  - `PYTHONPATH=src python -m pytest tests/test_qsim.py tests/test_run_real_mode.py`
  - Result: `50 passed`

## Smoke artifact
- `logs/ablation_runs/pairstate-synthetic-s42/metrics.json`
- `logs/ablation_runs/pairstate-synthetic-s42/run_diagnostics.json`

## Smoke readout
- accuracy: `1.0`
- F1: `1.0`
- positive-minus-negative offset gap: `0.482001`
- signed contrast mean: `0.067242`
- magnitude balance mean: `0.033282`
- sector-resolution-before-aggregation: `true`

## Immediate interpretation
- The bounded pair-state branch is executable.
- The required diagnostics are present.
- The branch now has enough implementation reality to justify the first full falsification packet.

## Files touched
- `src/qrope/qsim.py`
- `src/qrope/run.py`
- `tests/test_qsim.py`
- `tests/test_run_real_mode.py`

