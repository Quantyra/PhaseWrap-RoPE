# Research note

## Scope
- task:
  - `synthetic_dual_content_parity_coupling_binary`
- candidate:
  - `V_future_relational_witness_triple`
- controls:
  - `V_control_symbolic_sector_only`
  - `V_control_symbolic_content_only`
  - `V_control_symbolic_orientation_only`
  - `V_control_symbolic_sign_content_cross`
  - `V_control_symbolic_two_family_bounded`

## Writable scope
Only these files may change:
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## First packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- variants: candidate plus the five fixed controls
- local-only
- zero-credit

## Required diagnostics
- sector-family summaries
- content-family summaries
- orientation-family summaries
- sign/content/orientation agreement summaries
- parity label balance
- candidate feature order and coefficients
- control feature order and coefficients
- explicit proof that forbidden inputs are absent

## Stop rule
- if the candidate does not beat the strongest bounded control cleanly on the first packet, stop the branch and return to memo-only design
