# Q-RoPE Transition Orbit Signed-Margin Implementation v1

Date: 2026-03-11
Stories: S406

## Scope
- implemented `synthetic_transition_orbit_signed_margin_response`
- implemented `V_future_relational_witness_transition_orbit_signed_margin`
- implemented fixed bounded controls:
  - `V_control_symbolic_transition_signed_margin_lookup`
  - `V_control_symbolic_transition_signed_margin_cross_direction`
  - `V_control_symbolic_transition_signed_margin_quadratic`
  - `V_control_symbolic_transition_signed_margin_orbit_permuted`
- kept execution local-only on `sim_quantum_statevector`

## Code Changes
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Validation
- focused suite passed: `174 passed`

## Required Output
- summary CSV: `logs/ablation_runs/summary/transition_orbit_signed_margin_v1.csv`
