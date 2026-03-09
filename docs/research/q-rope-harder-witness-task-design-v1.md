# Research note

## Task direction
- Preserve one next task only: `synthetic_dual_content_parity_coupling_binary`

## Core idea
- Keep two observations and dual relational families.
- Make the label depend on a parity-style coupling between:
  - sector-sign agreement
  - content-family agreement
  - and one within-observation content-polarity term
- The next task should require a bounded head to combine information from:
  - cross-observation sector relation
  - cross-observation content relation
  - and one intra-observation content relation
- That should exceed the current bounded cross-family interaction control, which only sees the two boolean agreement variables.

## Why this is the right next memo
- The current harder task proved the branch can beat sector-only and content-only controls.
- It failed only when the control was allowed to see the exact cross-family agreement state directly.
- The next task should force one more relational degree of freedom without exploding scope.

## Protocol boundary
- Memo-only.
- No implementation approval in this step.
- No second alternative task family in parallel.
