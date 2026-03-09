# Q-RoPE Transition Orbit Rank-Band First Packet v1

Date: 2026-03-11
Stories: S361-S362

## Packet
- task: `synthetic_transition_orbit_rank_band_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- candidate: `V_future_relational_witness_transition_orbit_rank`
- controls:
  - `V_control_symbolic_transition_orbit_rank_lookup`
  - `V_control_symbolic_transition_cross_direction_regressor`
  - `V_control_symbolic_transition_quadratic_regressor`
  - `V_control_symbolic_transition_orbit_permuted_regressor`

## Generator Gate
Passed on all three seeds:
- `coarse_rank_lookup_near_null_pass = true`
- `within_state_rank_band_count_min = 4`
- `rank_band_balance_pass = true`

## Mean Results
- witness: MAE `0.322988`, rank correlation `0.673575`
- rank lookup: MAE `0.348522`, rank correlation `-1.000000`
- cross-direction: MAE `0.296917`, rank correlation `0.173205`
- quadratic: MAE `0.287255`, rank correlation `0.173205`
- orbit-permuted: MAE `0.301442`, rank correlation `0.076980`

## Interpretation
- The witness has the strongest ordinal signal by a wide margin.
- The witness does not lead on the primary metric.
- Two bounded symbolic controls (`quadratic`, `cross-direction`) and one orbit-aware control (`orbit-permuted`) all beat the witness on mean MAE.

## Packet Decision Input
Under the approved gate, this is a branch failure because the primary regression metric remains MAE. Stronger rank structure alone is not sufficient to keep the execution line active once multiple bounded controls outperform the witness on mean MAE.
