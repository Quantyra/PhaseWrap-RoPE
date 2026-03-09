# Phase-sensitive manifold implementation plan

## Scope
Implement one bounded local synthetic branch only.

## Task
- `synthetic_dual_phase_sensitive_manifold_response`

## Candidate
- `V_future_relational_witness_phase_sensitive`

## Controls
- `V_control_symbolic_coarse_lookup_regressor`
- `V_control_symbolic_analog_only_regressor`
- `V_control_symbolic_nonlinear_manifold_regressor`
- `V_control_symbolic_phase_insensitive_regressor`

## Writable scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## First packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- exactly fifteen runs total across candidate and controls

## Required diagnostics
- coarse tuple mean absolute max
- within-state variation flag
- target range summary
- feature audit for each control
- mean MAE and rank correlation per variant
- explicit proof that the phase-insensitive control omits state-conditioned phase offsets

## Anti-drift rules
- do not add lookup controls in this phase
- do not add a second phase-sensitive witness candidate
- do not expand beyond the fixed packet
