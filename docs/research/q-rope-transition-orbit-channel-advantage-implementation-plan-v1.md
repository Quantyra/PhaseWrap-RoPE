# Q-RoPE Transition Orbit Channel-Advantage Implementation Plan v1

Date: 2026-03-10
Stories: S450

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Fixed First Packet
- task: `synthetic_transition_orbit_channel_advantage_response`
- candidate: `V_future_relational_witness_transition_orbit_channel_advantage`
- controls:
  - `V_control_symbolic_transition_channel_lookup_regressor`
  - `V_control_symbolic_transition_channel_cross_direction_regressor`
  - `V_control_symbolic_transition_channel_quadratic_regressor`
  - `V_control_symbolic_transition_channel_orbit_permuted_regressor`
- seeds: `42`, `123`, `777`
- backend: `sim_quantum_statevector`

## Primary Metrics
- MAE
- rank correlation

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
