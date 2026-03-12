# Q-RoPE Transfer Fork-Join Approval Candidate v1

Date: 2026-03-12
Stories: S912

## BLUF
The `fork-join` line is a valid third transfer-family candidate because it is structurally different from both existing transfer families.

## Why It Qualifies
- It is not another path-local composition.
- It is not another loop-closure composition.
- It introduces branched relational structure plus a required rejoin operation.

## Allowed Symbolic Family
The first bounded control may use only:
- coarse fork-state indicators
- declared source-to-branch analog summaries
- declared branch-to-branch analog summaries
- declared branch-to-rejoin analog summaries
- one bounded quadratic layer over those declared summaries only

## Forbidden Family
The first bounded control may not use:
- latent fork-state ids
- exact microstate keys
- hidden branch tuple lookups
- uncontrolled basis growth

## Decision Status
- `APPROVAL-CANDIDATE`
- not implementation-approved in this step
