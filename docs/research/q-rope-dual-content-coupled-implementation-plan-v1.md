# Q-RoPE Dual Content-Coupled Implementation Plan v1

## Scope
- Story: `S200`
- Task:
  - `synthetic_dual_sector_content_agreement_binary`
- Candidate:
  - `V_future_relational_witness_dual_content`
- Controls:
  - `V_control_symbolic_dual_sector_interaction`
  - `V_control_symbolic_dual_content_interaction`
  - `V_control_symbolic_dual_cross_interaction`

## Writable scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

No other files may change for implementation logic.

## Task implementation rules
Add one new synthetic dataset mode only:
- `synthetic_dual_sector_content_agreement_binary`

The generator must emit diagnostics for:
- class balance
- sector-pair balance
- content-family balance
- sign-agreement counts
- content-agreement counts

## Candidate implementation rules
`V_future_relational_witness_dual_content` may use only:
- the existing dual witness sector-style features
- bounded content-family relational summaries
- a logistic-regression-equivalent head

It must not use:
- raw token identity beyond declared content-family mapping
- absolute positions
- numeric offsets as direct features

## Control implementation rules
### Sector-only interaction control
- sector-pair one-hot features only

### Content-only interaction control
- content-family pair one-hot features only

### Cross-family interaction control
- explicit interaction between:
  - sign-agreement
  - content-agreement
- still logistic-regression-equivalent only

## First packet
Run exactly:
- task `synthetic_dual_sector_content_agreement_binary`
- seeds `42`, `123`, `777`
- backend `sim_quantum_statevector`
- variants:
  - candidate
  - three controls

No extra seeds, tasks, or ablations in this step.

## Required diagnostics
All runs must emit:
- feature order
- coefficients
- intercept
- forbidden-input audit

Candidate must also emit:
- bounded feature audit

## Interpretation boundary
This first packet is about:
- whether the harder task still differentiates the branch from sector-only and content-only controls
- whether uniqueness collapses immediately under the cross-family interaction control

## Bottom line
The implementation phase is intentionally narrow.
If this packet is not interpretable, the branch should not broaden.
