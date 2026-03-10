# Q-RoPE Transition Orbit Sign-Flip Contrast Implementation Plan v1

Date: 2026-03-11
Stories: S432

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Fixed First Packet
- task: `synthetic_transition_orbit_sign_flip_contrast_binary`
- candidate: `V_future_relational_witness_transition_orbit_sign_flip_contrast`
- controls:
  - `V_control_symbolic_transition_flip_lookup`
  - `V_control_symbolic_transition_flip_cross_direction`
  - `V_control_symbolic_transition_flip_quadratic`
  - `V_control_symbolic_transition_flip_orbit_permuted`
- seeds: `42`, `123`, `777`
- backend: `sim_quantum_statevector`

## Primary Metrics
- accuracy
- F1

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
