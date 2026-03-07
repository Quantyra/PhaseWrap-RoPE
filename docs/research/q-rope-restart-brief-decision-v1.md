# Q-RoPE Restart Brief Decision v1

## Decision
- `APPROVE`
- implementation scope: `strictly limited`

Approve a new restart phase for:
- `V_new_explicit_interference`

Do not approve anything broader.

## What is approved
Approved:
- one bounded implementation phase
- local-only
- zero-credit
- synthetic packet only

Specifically approved:
- implement the constructive-vs-destructive interference comparator
- implement the parity-contrast observable
- run only the fixed synthetic falsification packet already defined

## What is not approved
Not approved:
- remote execution
- benchmark expansion
- cloud spend
- additional mechanism branches
- publication work

## Why approval is justified
The restart brief now meets the bar the repo has been enforcing:
1. materially new mechanism
2. explicit theorem link
3. explicit observable
4. explicit synthetic falsification packet
5. explicit stop rules

That is enough to justify one disciplined implementation attempt.

## Why scope must stay narrow
The initiative already burned substantial time on underpowered or ambiguous branches.

The only rational reopening is:
- one falsifiable implementation pass
- under the exact fixed packet
- with no room for scope drift

## Approval conditions
This approval remains valid only if all are obeyed:
1. implementation changes stay inside the minimal boundary declared in the restart brief
2. no new datasets or benchmarks are introduced
3. no remote code path is touched
4. pass/fail rules remain unchanged
5. if the result is mixed or score-shift-only, the restart stops immediately

## Immediate next step
Open implementation planning only for:
- `V_new_explicit_interference`

That planning step should specify:
- exact files to change
- exact diagnostics to emit
- exact test additions

## Bottom line
The brief is strong enough.
Quantyra should allow one tightly bounded implementation attempt under the existing synthetic falsification gate.
