# Restart scaffold for nonlinear manifold task

## Task
- `synthetic_dual_nonlinear_manifold_response`

## Future candidate
- `V_future_relational_witness_nonlinear`

## Fixed future controls
- `V_control_symbolic_coarse_lookup_regressor`
- `V_control_symbolic_analog_only_regressor`
- `V_control_symbolic_full_declared_additive_regressor`

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
- proof that additive controls do not include nonlinear interaction terms

## Future gate
Do not approve implementation unless the task memo and scaffold together show both:
- coarse lookup is near-null by construction
- the additive analog baseline is intentionally insufficient by construction
