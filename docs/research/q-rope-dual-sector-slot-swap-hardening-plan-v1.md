# Q-RoPE Dual-Sector Slot-Swap Hardening Plan v1

## Scope
- Story: `S180`
- Task: `synthetic_dual_sector_agreement_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Variants:
  - `V_future_relational_witness_dual`
  - `V_control_symbolic_dual_sector`

## Control definition
Apply one deterministic sample-level transform before model execution:
- swap observation `A` and observation `B`

Specifically, for every synthetic sample:
- exchange all `a_*` fields with the corresponding `b_*` fields
- keep the label unchanged

## Why the label stays unchanged
The task label depends on same-sign agreement between `sector_a` and `sector_b`.
That predicate is symmetric under exchange of the two observation slots.

So slot swapping should preserve:
- task meaning
- class balance
- sector-pair balance

## Exact packet
Rerun the same six-run packet under:
- `slot_swap = 1`
- seeds `42`, `123`, `777`
- same candidate and same control only

## Required outputs
For the swapped packet, emit:
- mean accuracy
- mean F1
- generator diagnostics including `slot_swap`
- the same witness/control diagnostics already required in the first packet

## Interpretation rule
### Pass
The branch gets stronger if:
- the candidate remains clearly ahead of the control
- and the candidate does not materially degrade relative to the original packet

### Fail
The branch weakens if:
- the candidate collapses toward the control
- or the control catches up under slot swap

## What is explicitly not allowed
- new tasks
- new variants
- extra control families
- remote execution

## Bottom line
This is one bounded symmetry check.
If the branch survives it, the agreement interpretation becomes materially stronger.
