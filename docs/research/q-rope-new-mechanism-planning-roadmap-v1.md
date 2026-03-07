# Q-RoPE New Mechanism Planning Roadmap v1

## Purpose
Open a disciplined planning track for a future mechanism proposal without reopening experiments.

This roadmap exists to prevent two failure modes:
- vague mechanism ideation
- premature implementation before falsification is explicit

## Planning sequence

### S098
`Mechanism family selection`

Goal:
- choose one concrete mechanism family to plan first

Initial recommendation:
- `explicit relative-phase interference comparator`

Alternative families remain secondary:
- observable-family redesign
- architecture-level query-key redesign

### S099
`State-preparation design memo`

Goal:
- specify exactly how token content and positional phase enter branch `A` and branch `B`

Deliverable:
- implementation-ready state-preparation section for the restart brief

### S100
`Comparator/interference design memo`

Goal:
- specify the exact interference or contrast primitive

Deliverable:
- one explicit comparison design
- one explicit reason it is not equivalent to the failed pairwise-overlap branch

### S101
`Observable and readout design memo`

Goal:
- specify the observable that is supposed to separate relative-phase contrast from global score elevation

Deliverable:
- one observable definition
- one failure analysis if the observable collapses into a score-shift proxy

### S102
`Synthetic falsification packet memo`

Goal:
- bind the new mechanism to a small, predeclared theorem-validation packet

Deliverable:
- exact seeds
- exact dataset
- exact diagnostics
- exact pass/fail rules

### S103
`Implementation-readiness review`

Goal:
- decide whether the proposal is specific enough to justify a future restart brief submission

Deliverable:
- `GO` to write the restart brief
- or `HOLD` if the mechanism remains too vague

## Guardrails
- no code
- no experiments
- no remote execution
- no cloud spend
- no benchmark expansion

## Bottom line
The next phase is not “restart the project.”
It is:
- plan one new mechanism carefully enough that a future restart brief could be judged on technical merit.
