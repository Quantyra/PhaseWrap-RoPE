# Orthogonalized continuous restart scaffold

## Preserved path
- task: `synthetic_dual_orthogonalized_continuous_response`
- future candidate: `V_future_relational_witness_orthogonalized`

## Future required controls
- `V_control_symbolic_coarse_lookup_regressor`
- `V_control_symbolic_analog_only_regressor`
- `V_control_symbolic_full_declared_residual_regressor`

## Future gate requirements
Before any implementation is approved, a future memo must show:
- coarse lookup is intentionally near-null by task construction
- analog-only control is not trivially sufficient for perfect performance
- the full declared residual regressor is explicit enough to make the packet fair

## Fixed future first packet posture
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit
- one candidate only
