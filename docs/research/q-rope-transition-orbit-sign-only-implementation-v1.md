# Q-RoPE Transition Orbit Sign-Only Implementation v1

Date: 2026-03-11
Stories: S415

## Scope
- implemented `synthetic_transition_orbit_sign_only_binary`
- implemented `V_future_relational_witness_transition_orbit_sign_only`
- implemented fixed bounded controls:
  - `V_control_symbolic_transition_sign_lookup`
  - `V_control_symbolic_transition_sign_cross_direction`
  - `V_control_symbolic_transition_sign_quadratic`
  - `V_control_symbolic_transition_sign_orbit_permuted`
- kept execution local-only on `sim_quantum_statevector`

## Code Changes
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Validation
- focused suite passed: `177 passed`

## Required Output
- summary CSV: `logs/ablation_runs/summary/transition_orbit_sign_only_v1.csv`
