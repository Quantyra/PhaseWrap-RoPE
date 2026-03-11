# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Flip Persistence Implementation v1

Date: 2026-03-11
Stories: S613

## Scope
- implemented `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary`
- reused the slot-invariant top-k pair-order stability generator as the bounded latent source
- exposed signed-flip persistence diagnostics and routed the fixed control stack through the existing order backend

## Files Changed
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Validation
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- result: `240 passed`
