# Q-RoPE E008 Exception Arbitration Implementation v1

Date: 2026-03-16
Stories: S1518-S1521

## Scope
- Implemented `synthetic_positional_exception_conditioned_reference_selection_response` inside the frozen E008 scope.
- Added the witness path, bounded symbolic control path, dataset loader wiring, and focused tests.
- Kept one symbolic family across candidate counts `4` and `5` with exactly one active exception trigger per accepted example.

## Notes
- The accepted generator uses one suppressed base-match plus one surviving base-match under a candidate-local exception trigger derived from `orientation_delta`.
- The exception remains auditable from existing path features and does not use explicit exception ids or lookup tables.
- The runtime path uses a compact witness basis and a single frozen symbolic family across exception patterns.

## Validation
- Focused synthetic and real-mode tests passed before the packet run.
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- `351 passed`
