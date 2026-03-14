# Q-RoPE Realism-Bridge Offset-Retrieval Implementation v1

## Scope
- Implemented `synthetic_positional_offset_retrieval_response` inside the frozen writable scope only.

## Files Changed
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Implementation Summary
- Added the offset-retrieval realism-bridge generator.
- Added dataset rendering/parsing for `anchor -> target -> distractor -> resolve`.
- Added the bounded witness and symbolic control feature paths.
- Added focused tests for bundle diagnostics and real-mode backends.

## Validation
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- `324 passed`

## Summary CSV
- `logs/ablation_runs/summary/realism_bridge_offset_retrieval_v1.csv`
