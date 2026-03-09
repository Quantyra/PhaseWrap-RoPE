# Q-RoPE Transition Orbit Rank-Band Decision Memo v1

Date: 2026-03-11
Stories: S362-S363

## Decision
Stop the `synthetic_transition_orbit_rank_band_response` execution branch.

## Why
The corrected packet is valid, but the candidate fails the active gate:
- witness MAE `0.322988`
- strongest control MAE `0.287255` (`V_control_symbolic_transition_quadratic_regressor`)
- second strongest control MAE `0.296917` (`V_control_symbolic_transition_cross_direction_regressor`)
- orbit-aware permuted control MAE `0.301442`

The witness does retain the strongest mean rank correlation (`0.673575`), but this line was approved under a primary-metric rule where rank correlation is diagnostic support, not a replacement for MAE leadership.

## Consequence
- do not widen the control family on this task
- do not reopen hardening on this task
- return the line to memo-only posture

## Preserved Signal
One result remains worth preserving:
- the witness captures ordinal structure substantially better than the bounded symbolic controls

That supports a new memo-only direction where the target is explicitly order-focused rather than magnitude-regression-focused.
