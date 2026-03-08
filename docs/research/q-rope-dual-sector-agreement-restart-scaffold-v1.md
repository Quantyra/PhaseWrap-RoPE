# Q-RoPE Dual-Sector Agreement Restart Scaffold v1

## Scope
- Story: `S174`
- Status: memo-only

## Task
- `synthetic_dual_sector_agreement_binary`

## Candidate branch
- `V_future_relational_witness_dual`

## Candidate branch interpretation
This is not a brand-new broad architecture family.
It is the next bounded continuation of the witness line under a harder task.

What should remain conceptually fixed:
- sector-first relational representation
- compact contrast-oriented witness feature extraction
- tiny logistic-regression-equivalent head only

What changes:
- two relational observations per sample instead of one
- label depends on agreement across the two sector assignments

## Allowed symbolic control
- `V_control_symbolic_dual_sector`

Control definition remains fixed:
- separate one-hot block for `sector_a`
- separate one-hot block for `sector_b`
- same tiny logistic head
- no cross terms
- no hidden layer

## First future packet
If later approved, the first packet must remain:
- local-only
- zero-credit
- seeds `42`, `123`, `777`
- exactly two variants:
  - `V_future_relational_witness_dual`
  - `V_control_symbolic_dual_sector`

## First future gate
The candidate branch must show all of these:
- beat the symbolic control on mean accuracy and mean F1
- hold across all three seeds without one-seed collapse
- preserve bounded-feature and no-shortcut audit rules

## Explicit failure rule
Do not reopen broader experimentation if:
- the symbolic control matches the candidate
- or the candidate only wins through a broader or less disciplined input schema

## Why this scaffold matters
The previous task failed as a uniqueness test because the symbolic control was too strong for that label rule.

This scaffold prevents the next attempt from drifting by fixing:
- one harder task
- one candidate branch
- one control
- one first packet

## Bottom line
The witness branch now has a disciplined next target.
Any future implementation proposal should be judged only against this scaffold, not against a looser continuation of the old task.
