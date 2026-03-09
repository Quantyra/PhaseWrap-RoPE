# Q-RoPE Dual-Sector Token-Renaming Hardening Plan v1

## Scope
- Story: `S183`
- Task: `synthetic_dual_sector_agreement_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Variants:
  - `V_future_relational_witness_dual`
  - `V_control_symbolic_dual_sector`

## Control definition
Apply one deterministic global token permutation before model execution:
- `A -> C`
- `B -> D`
- `C -> A`
- `D -> B`

The same permutation must be applied to:
- observation `A`
- observation `B`
- every split
- every seed

## Why the label stays unchanged
The task label depends only on agreement between:
- `sector_a`
- `sector_b`

It does not depend on token identity.

So token renaming should preserve:
- task meaning
- class balance
- sector-pair balance
- slot balance

## Exact packet
Rerun the same six-run packet under:
- `token_permutation = cdab`
- seeds `42`, `123`, `777`
- same candidate and same control only

## Required outputs
For the renamed packet, emit:
- mean accuracy
- mean F1
- generator diagnostics including `token_permutation`
- the same witness/control diagnostics already required in the first packet

## Interpretation rule
### Pass
The branch gets stronger if:
- the candidate remains clearly ahead of the control
- and the candidate does not materially degrade relative to the original packet

### Fail
The branch weakens if:
- the candidate collapses toward the control
- or the control catches up under token renaming

## What is explicitly not allowed
- new tasks
- new variants
- extra control families
- remote execution

## Bottom line
This is one bounded lexical-invariance check.
If the branch survives it, the current result becomes materially less vulnerable to token-identity explanations.
