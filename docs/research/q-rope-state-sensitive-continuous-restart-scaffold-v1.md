# State-sensitive continuous restart scaffold

## Preserved path
- task: `synthetic_dual_state_sensitive_continuous_response`
- future candidate: `V_future_relational_witness_state_sensitive`

## Future required controls
- `V_control_symbolic_coarse_lookup_regressor`
  - sees only the three coarse agreement bits
- `V_control_symbolic_analog_only_regressor`
  - sees only the two new analog factors
- `V_control_symbolic_full_declared_regressor`
  - sees the full declared future symbolic feature set

## Fixed first-packet posture
If this path is ever approved:
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit
- one candidate only

## Approval condition for future reopening
Do not approve implementation until a future memo proves both:
- the task genuinely varies within coarse agreement states
- the future control stack is explicit enough to test whether the witness branch contributes beyond declared symbolic features
