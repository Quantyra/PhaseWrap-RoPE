# Q-RoPE Transfer Relay-Binding Plan Decision v1

Date: 2026-03-12
Stories: S967

## Decision
- the relay-binding line is specific enough for one bounded implementation cycle
- code may reopen only inside the frozen writable scope defined in the implementation plan

## Why
- the task, witness, symbolic control family, diagnostics, and stop rule are all explicit
- the plan preserves the same bounded execution discipline used by the preserved transfer families

## Next Valid Move
- implement the relay-binding task inside the frozen scope
- run the fixed three-seed packet
- stop the line immediately if the bounded symbolic control clears the active two-metric gate
