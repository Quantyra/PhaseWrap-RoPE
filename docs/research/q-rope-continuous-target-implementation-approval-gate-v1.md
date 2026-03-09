# Research note

## Decision
- `APPROVE`
- scope: strictly limited

## Approved scope
- one local-only implementation phase
- one synthetic task only:
  - `synthetic_dual_continuous_coupled_response`
- one candidate only:
  - `V_future_relational_witness_continuous`
- one fixed bounded regression control stack only
- one first packet only:
  - seeds `42`, `123`, `777`

## Explicitly disallowed
- remote execution
- benchmark expansion
- additional candidates
- parallel side branches
- publication work

## Reason
- the task/control package is now specific enough that a bounded regression phase is falsifiable and auditable
- the branch should now be tested, not extended by more memo drift
