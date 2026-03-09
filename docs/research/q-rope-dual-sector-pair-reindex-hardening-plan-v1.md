# Q-RoPE Dual-Sector Pair-Reindex Hardening Plan v1

## Scope
- Story: `S189`
- Task: `synthetic_dual_sector_agreement_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Variants:
  - `V_future_relational_witness_dual`
  - `V_control_symbolic_dual_sector`

## Control definition
Apply one deterministic intra-bucket pairing transform before model execution:
- `pair_reindex = 1`

For every `(sector_a, sector_b)` bucket:
- keep the selected `sample_a` list unchanged
- rotate the selected `sample_b` list by one position before pairing

So pairing changes from:
- `(a_0, b_0), (a_1, b_1), (a_2, b_2), (a_3, b_3)`

to:
- `(a_0, b_1), (a_1, b_2), (a_2, b_3), (a_3, b_0)`

## Why the label stays unchanged
The task label depends only on sign-family agreement between:
- `sector_a`
- `sector_b`

All samples inside a sector bucket share the same sector identity.
So changing the concrete within-bucket pairing changes examples, but not:
- task meaning
- class balance
- sector-pair balance
- sector-slot balance

## Why this control is better than split rotation
`split_rotation = 1` was inert under the current generator structure.

`pair_reindex = 1` is not inert:
- it changes the paired concrete examples directly
- while leaving the sector structure fixed

## Exact packet
Rerun the same six-run packet under:
- `pair_reindex = 1`
- seeds `42`, `123`, `777`
- same candidate and same control only

## Required outputs
For the reindexed packet, emit:
- mean accuracy
- mean F1
- generator diagnostics including `pair_reindex`
- the same witness/control diagnostics already required in the first packet

## Interpretation rule
### Pass
The branch gets stronger if:
- the candidate remains clearly ahead of the control
- and the candidate does not materially degrade relative to the prior packets

### Fail
The branch weakens if:
- the candidate collapses materially
- or the control catches up under pair reindexing

## What is explicitly not allowed
- new tasks
- new variants
- extra control families
- remote execution

## Bottom line
This is the first meaningful concrete-pairing robustness check for the dual-sector branch.
