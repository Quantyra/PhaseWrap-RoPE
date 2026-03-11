# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Flip Recurrence Implementation v1

Date: 2026-03-11
Stories: S622

## Scope
- implemented the bounded `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary` branch only
- local-only
- zero-credit
- fixed three-seed packet

## Changes
- added the recurrence dataset wrapper in `src/qrope/synthetic.py`
- routed the witness and bounded symbolic controls through `src/qrope/run.py`
- added focused loader and diagnostics tests in `tests/test_synthetic.py` and `tests/test_run_real_mode.py`

## Validation
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- result: `243 passed`
