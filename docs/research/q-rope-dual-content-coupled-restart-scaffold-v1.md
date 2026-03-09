# Q-RoPE Dual Content-Coupled Restart Scaffold v1

## Scope
- Story: `S197`
- Task:
  - `synthetic_dual_sector_content_agreement_binary`
- Status:
  - memo-only

## Fixed future candidate
- `V_future_relational_witness_dual_content`

The future candidate is still conceptual only.
It must be constrained to:
- sector-first relational summaries
- content-family relational summaries
- bounded witness-style head

## Fixed future controls
Any later approval must compare the candidate against exactly these control families:

1. `V_control_symbolic_dual_sector_interaction`
- uses sector-family interaction terms only
- no content-family features

2. `V_control_symbolic_dual_content_interaction`
- uses content-family interaction terms only
- no sector-family features

3. `V_control_symbolic_dual_cross_interaction`
- uses both sector-family and content-family variables with explicit interaction terms
- still logistic-regression-equivalent only
- no token identity beyond the declared content-family partition
- no absolute positions
- no numeric offsets

## Why all three controls are required
The harder task only means anything if a future packet can separate:
- sector-only sufficiency
- content-only sufficiency
- cross-family sufficiency

Without that, the next branch would repeat the same ambiguity that exhausted the earlier dual task.

## Fixed future packet
If later approved, the first packet must remain:
- local-only
- zero-credit
- seeds `42`, `123`, `777`
- one candidate only
- the three fixed control families only

## Fixed future decision rule
The future candidate is only interesting if it beats:
- sector-only control
- content-only control

and is not trivially matched by:
- cross-family control

If the cross-family control matches it exactly on the first packet:
- uniqueness is exhausted immediately

## What remains disallowed
- implementation in this step
- remote execution
- additional task families
- extra baseline sprawl

## Bottom line
The harder dual content-coupled task now has one fixed future scaffold.
That is enough for a later approval review, but not enough to justify code yet.
