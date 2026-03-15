# Q-RoPE Successor Key-Query Offset Selection Implementation v1

## Scope
- Implemented `synthetic_positional_key_query_offset_selection_response` inside the frozen writable scope only.

## Files Changed
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Implementation Summary
- Added the bounded key-query offset-selection generator with one query and four bounded candidates.
- Defined the target by a query-relative positional rule so the task stays genuinely one-of-many rather than target-vs-distractor only.
- Added rendering and parsing for `q | c0 | c1 | c2 | c3` packets.
- Added the bounded witness and symbolic control feature paths.
- Tightened the witness/control basis after the first implementation attempt exposed numerical blow-up from an over-complete feature family.
- Added focused diagnostics and real-mode coverage for the successor candidate.

## Validation
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- `327 passed`

## Summary CSV
- `logs/ablation_runs/summary/successor_key_query_offset_selection_v1.csv`
