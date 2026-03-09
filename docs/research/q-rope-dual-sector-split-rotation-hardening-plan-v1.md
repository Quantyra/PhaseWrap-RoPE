# Q-RoPE Dual-Sector Split-Rotation Hardening Plan v1

## Scope
- Story: `S186`
- Task: `synthetic_dual_sector_agreement_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Variants:
  - `V_future_relational_witness_dual`
  - `V_control_symbolic_dual_sector`

## Control definition
Apply one deterministic split-selection transform before model execution:
- `split_rotation = 1`

This rotates the selected example within each balanced bucket while preserving:
- class counts
- sector-pair counts
- sector-slot counts
- label rule

## Why this control matters
The branch has already survived:
- slot symmetry
- global token renaming

The next unresolved risk is that the current win depends on one favorable deterministic within-bucket sample choice.

Split rotation changes:
- which concrete examples appear in each split

without changing:
- the task
- the candidate
- the control
- the fixed packet size

## Exact packet
Rerun the same six-run packet under:
- `split_rotation = 1`
- seeds `42`, `123`, `777`
- same candidate and same control only

## Required outputs
For the rotated packet, emit:
- mean accuracy
- mean F1
- generator diagnostics including `split_rotation`
- the same witness/control diagnostics already required in the first packet

## Interpretation rule
### Pass
The branch gets stronger if:
- the candidate remains clearly ahead of the control
- and the candidate does not materially degrade relative to the prior packets

### Fail
The branch weakens if:
- the candidate degrades sharply
- or the control catches up under split rotation

## What is explicitly not allowed
- new tasks
- new variants
- extra control families
- remote execution

## Bottom line
This is one bounded sample-selection robustness check.
If the branch survives it, the current line becomes materially stronger as an internal mechanism result.
