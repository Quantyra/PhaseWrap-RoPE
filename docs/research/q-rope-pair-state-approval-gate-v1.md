# Q-RoPE Pair-State Approval Gate v1

## Decision
- `APPROVE`
- scope: `strictly limited`

Approve one bounded implementation phase for:
- `V_pairstate_relational`

Do not approve anything broader.

## What is approved
Approved:
- one local-only implementation phase
- one synthetic-only falsification packet
- one candidate variant: `V_pairstate_relational`
- one backend family: local simulator only

Specifically approved:
- implement the pair-state content/sector/coupling construction
- implement sector-resolved signed-response measurement
- run only the fixed synthetic packet already defined

## What is not approved
Not approved:
- remote execution
- benchmark expansion
- cloud spend
- multiple variant branching
- publication work

## Why approval is justified
The pair-state direction now clears the paper-level bar the repo has been enforcing:
1. materially new mechanism
2. explicit representation
3. explicit sector scheme
4. explicit measurement ordering
5. explicit falsification packet
6. explicit anti-collapse rule

That is enough to justify one disciplined implementation attempt.

## Why scope must stay narrow
The repo already paid the cost of reopening weak ideas too early.

The only rational next move is:
- one bounded implementation
- under one fixed packet
- with immediate stop conditions

## Approval conditions
This approval remains valid only if all are obeyed:
1. implementation changes stay inside the minimal boundary declared in the brief
2. no remote code path is touched
3. no new datasets or benchmark branches are introduced
4. diagnostics expose sector responses before aggregation
5. any pooled-score collapse fails the branch immediately

## Immediate next step
Open implementation planning only for:
- `V_pairstate_relational`

That planning step should specify:
- exact files to change
- exact diagnostics to emit
- exact tests to add

## Bottom line
The pair-state direction is the first post-archive angle that is specific enough to deserve one bounded implementation phase.
Approve that phase, and nothing broader.

