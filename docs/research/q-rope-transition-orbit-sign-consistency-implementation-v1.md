# Q-RoPE Transition Orbit Sign-Consistency Implementation v1

Date: 2026-03-11
Stories: S424

## Scope
- implemented the bounded local-only branch for `synthetic_transition_orbit_sign_consistency_binary`
- no remote execution
- no task expansion
- no additional control families

## Files Changed
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Generator Contract
- `coarse_consistency_lookup_near_null_pass = true`
- `within_state_consistency_variation_pass = true`
- `paired_context_diversity_pass = true`
- `consistency_label_balance_pass = true`
- `token_view_balance_pass = true`

## Validation
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- result: `180 passed`

## Packet Artifact Root
- `logs/ablation_runs/summary/transition_orbit_sign_consistency_v1.csv`
