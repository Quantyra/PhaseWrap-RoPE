# Q-RoPE Transition Orbit Rank-Band Implementation v1

Date: 2026-03-11
Story: S361

## Scope
Implemented the bounded local-only rank-band transition-orbit branch for:
- task: `synthetic_transition_orbit_rank_band_response`
- candidate: `V_future_relational_witness_transition_orbit_rank`
- controls:
  - `V_control_symbolic_transition_orbit_rank_lookup`
  - `V_control_symbolic_transition_cross_direction_regressor`
  - `V_control_symbolic_transition_quadratic_regressor`
  - `V_control_symbolic_transition_orbit_permuted_regressor`

## Code Changes
- added `generate_transition_orbit_rank_band_response_bundle(...)` to [synthetic.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/synthetic.py)
- added rank-band witness/control routing to [run.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/run.py)
- added focused generator and loader tests in [test_synthetic.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/tests/test_synthetic.py) and [test_run_real_mode.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/tests/test_run_real_mode.py)

## Generator Correction
The first implementation collapsed for seeds `123` and `777` because coarse transition buckets were filtered by exact cardinality after indirect sector-pair grouping.

The corrected implementation:
- groups candidates globally by coarse transition state first
- selects four spread-out band points per coarse state
- alternates split assignment by coarse-state parity so train means stay fixed at `0.5` while validation and test retain ordinal variation
- routes `V_control_symbolic_transition_orbit_permuted_regressor` through the orbit-aware backend for this dataset so `run_diagnostics.json` is emitted consistently

## Validation
Command:
`PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`

Result:
`162 passed`

## Packet Artifacts
Raw packet runs:
- `orbit-rank-witness-s42/s123/s777`
- `orbit-rank-lookup-s42/s123/s777`
- `orbit-rank-xdir-s42/s123/s777`
- `orbit-rank-quad-s42/s123/s777`
- `orbit-rank-perm-s42/s123/s777`

Summary:
- [transition_orbit_rank_band_v1.csv](C:/Users/Dan/Desktop/Projects/QuantyraQRope/logs/ablation_runs/summary/transition_orbit_rank_band_v1.csv)
