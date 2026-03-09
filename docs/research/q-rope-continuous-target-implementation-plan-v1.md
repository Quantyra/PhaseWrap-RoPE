# Research note

## Scope
- task:
  - `synthetic_dual_continuous_coupled_response`
- candidate:
  - `V_future_relational_witness_continuous`
- controls:
  - `V_control_symbolic_single_family_regressor`
  - `V_control_symbolic_two_family_regressor`
  - `V_control_symbolic_boolean_state_lookup`

## Writable scope
Only these files may change:
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## First packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- variants: candidate plus the three fixed controls
- local-only
- zero-credit

## Required diagnostics
- target distribution summary
- sector/content/orientation family summaries
- agreement summaries
- candidate feature order and coefficients
- control feature order and coefficients
- mean absolute error
- rank correlation
- calibration slope or linear fit summary
- explicit proof that forbidden inputs are absent

## Stop rule
- if the candidate does not beat the bounded symbolic regressors and stay competitive with the boolean-state lookup baseline on the first packet, stop the branch and return to memo-only design
