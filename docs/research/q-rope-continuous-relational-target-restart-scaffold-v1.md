# Research note

## Future restart scaffold
- task:
  - `synthetic_dual_continuous_coupled_response`
- future candidate:
  - `V_future_relational_witness_continuous`
- fixed future controls:
  - `V_control_symbolic_single_family_regressor`
  - `V_control_symbolic_two_family_regressor`
  - `V_control_symbolic_boolean_state_lookup`

## First packet posture
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- mode:
  - local-only
  - zero-credit
- no remote work
- no benchmark expansion
- no second candidate in parallel

## Evaluation posture
- primary metric:
  - mean absolute error
- secondary metrics:
  - rank correlation
  - calibration slope
- no publication or expansion unless the candidate is both accurate and better calibrated than the bounded symbolic controls

## Current status
- preserved
- not approval-candidate yet
- memo-only
