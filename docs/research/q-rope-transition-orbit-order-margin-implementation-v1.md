# Q-RoPE Transition Orbit Order-Margin Implementation v1

Date: 2026-03-11
Stories: S397

## Scope
- implemented `synthetic_transition_orbit_order_margin_response`
- implemented `V_future_relational_witness_transition_orbit_order_margin`
- implemented fixed bounded controls:
  - `V_control_symbolic_transition_margin_lookup`
  - `V_control_symbolic_transition_margin_cross_direction`
  - `V_control_symbolic_transition_margin_quadratic`
  - `V_control_symbolic_transition_margin_orbit_permuted`
- kept execution local-only on `sim_quantum_statevector`

## Code Changes
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `src/qrope/aggregate.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Important Implementation Note
- the first order-margin generator pass incorrectly collapsed within-state margin variation
- the implementation was corrected by assigning a centered four-level margin template within each coarse state
- after correction, the hard-stop generator diagnostics passed on all seeds

## Validation
- focused suite passed: `171 passed`

## Required Output
- summary CSV: `logs/ablation_runs/summary/transition_orbit_order_margin_v1.csv`
