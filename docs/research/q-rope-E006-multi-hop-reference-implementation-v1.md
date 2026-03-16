# Q-RoPE E006 Multi-Hop Reference Implementation v1

Date: 2026-03-16
Stories: S1454-S1457

## Scope
- Implemented `synthetic_positional_intermediate_pointer_selection_response` inside the frozen E006 scope.
- Added the witness path, bounded symbolic control path, dataset loader wiring, and focused tests.
- Kept one symbolic family across candidate counts `4` and `5` with exactly two hop depth.

## Notes
- The final generator uses a genuinely decision-critical intermediate hop and blocks direct query-to-target collapse.
- The first E006 draft overpartitioned state buckets by intermediate and target slot, which yielded an empty dataset bundle.
- The accepted implementation keeps slot diversity as a diagnostic while freezing the coarse state buckets at the multi-hop decision layer.

## Validation
- Focused synthetic and real-mode tests passed before the packet run.
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- `345 passed`
