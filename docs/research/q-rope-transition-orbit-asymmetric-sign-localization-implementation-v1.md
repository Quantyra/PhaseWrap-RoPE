# Q-RoPE Transition Orbit Asymmetric Sign-Localization Implementation v1

Date: 2026-03-11
Stories: S442

## Scope
- implemented the bounded local-only branch for `synthetic_transition_orbit_asymmetric_sign_localization_binary`
- no remote execution
- no task expansion
- no additional control families

## Files Changed
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Generator Contract
- `coarse_localization_lookup_near_null_pass = true`
- `within_state_localization_variation_pass = true`
- `paired_channel_diversity_pass = true`
- `localization_label_balance_pass = true`
- `token_view_balance_pass = true`

## Validation
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- result: `186 passed`

## Packet Artifact Root
- `logs/ablation_runs/summary/transition_orbit_asymmetric_sign_localization_v1.csv`
