# Restart scaffold for phase-sensitive manifold task

## Task
- `synthetic_dual_phase_sensitive_manifold_response`

## Future candidate
- `V_future_relational_witness_phase_sensitive`

## Fixed future controls
- `V_control_symbolic_coarse_lookup_regressor`
- `V_control_symbolic_analog_only_regressor`
- `V_control_symbolic_nonlinear_manifold_regressor`
- `V_control_symbolic_phase_insensitive_regressor`

## Fixed first packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit

## Required diagnostics
- coarse tuple mean absolute max
- within-state variation flag
- candidate/control mean MAE
- candidate/control rank correlation
- proof that the phase-insensitive control excludes state-conditioned phase offsets

## Future gate
Do not approve implementation unless the task memo and scaffold together show all of the following:
- coarse lookup is near-null by construction
- additive analog baselines are intentionally insufficient
- the current direct nonlinear control family is intentionally insufficient
- the new phase-insensitive control does not quietly smuggle state-conditioned phase offsets back in
