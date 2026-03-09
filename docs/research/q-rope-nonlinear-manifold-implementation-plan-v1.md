# Nonlinear manifold implementation plan

## Scope
Implement one bounded local synthetic branch only.

## Task
- `synthetic_dual_nonlinear_manifold_response`

## Candidate
- `V_future_relational_witness_nonlinear`

## Controls
- `V_control_symbolic_coarse_lookup_regressor`
- `V_control_symbolic_analog_only_regressor`
- `V_control_symbolic_full_declared_additive_regressor`

## Writable scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## First packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- exactly twelve runs total across candidate and controls

## Required diagnostics
- coarse tuple mean absolute max
- within-state variation flag
- target range summary
- feature audit for each control
- mean MAE and rank correlation per variant

## Anti-drift rules
- do not add nonlinear symbolic controls in this phase
- do not add a second nonlinear witness candidate
- do not expand beyond the fixed packet
