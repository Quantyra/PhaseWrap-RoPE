# Q-RoPE Bridge Anchor-Offset-Signature Implementation v1

## Scope
- Implemented `synthetic_positional_anchor_offset_signature_response` inside the frozen writable scope only.

## Files Changed
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Implementation Summary
- Added the anchor-relative offset-signature bridge-task generator.
- Added dataset rendering/parsing for `anchor -> probe -> alternate -> resolve`.
- Added the bounded witness and symbolic control feature paths.
- Added focused tests for bundle diagnostics and real-mode backends.

## Validation
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- `318 passed`
