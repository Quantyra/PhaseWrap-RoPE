# Q-RoPE Transition Orbit Signed-Margin Implementation Plan v1

Date: 2026-03-11
Stories: S405

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Fixed First Packet
- task: `synthetic_transition_orbit_signed_margin_response`
- candidate: `V_future_relational_witness_transition_orbit_signed_margin`
- controls:
  - `V_control_symbolic_transition_signed_margin_lookup`
  - `V_control_symbolic_transition_signed_margin_cross_direction`
  - `V_control_symbolic_transition_signed_margin_quadratic`
  - `V_control_symbolic_transition_signed_margin_orbit_permuted`
- seeds: `42`, `123`, `777`
- backend: `sim_quantum_statevector`

## Primary Metrics
- mean absolute error
- sign agreement accuracy

## Required Outputs
- implementation note
- first packet memo
- decision memo
- summary CSV
- generator diagnostics for every run

## Prohibitions
- no remote adapters
- no broader task family changes
- no additional controls
- no uncontrolled metric changes
