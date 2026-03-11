# Q-RoPE Symbolic Insufficiency Dual-Atlas Transition-Bilinear Plan Decision v1

Date: 2026-03-11
Stories: S768

## Decision
- the dual-atlas transition-bilinear line is specific enough for one bounded implementation cycle
- reject any broader code reopening in this step

## Why
- the challenger family is now mechanically frozen at plan level
- lattice size, chart rules, residual definitions, bilinear definitions, transition-residual definitions, and transition-bilinear definitions are explicit
- the standing witness benchmark and fixed packet metrics are unchanged

## Operational Consequence
- next valid move is to implement exactly one challenger:
  - `V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_bilinear`
- writable scope stays limited to:
  - `src/qrope/run.py`
  - `tests/test_run_real_mode.py`
- do not add a second challenger or broaden the packet
