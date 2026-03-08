# Q-RoPE Pair-State Restart Decision v1

## Decision
- `PRESERVE`
- `DO NOT APPROVE YET`

## Meaning
The pair-state angle is now the strongest preserved future restart direction in the repository.

It is not approved for implementation.

## Why preserve it
- It is materially different from the stopped branch-local scoring path.
- It changes both representation and observable.
- It is the first post-archive angle that is specific enough to be falsifiable without drifting into broad benchmark work.

## Why not approve it yet
- The idea is still only memo-level.
- There is no proof yet that the proposed pair-state sectors can be implemented cleanly in the current local simulator path without collapsing back into another indirect score proxy.
- The exact sector definition and measurement operator remain design-level, not execution-level.

## Correct posture
Correct current posture:
- keep the brief
- keep the scaffold
- keep the falsification packet
- do not code it
- do not run it

## What would justify future approval
Approval would be justified only if a later memo closes the remaining design gaps:
1. exact sector definition
2. exact measurement rule
3. exact aggregation rule
4. explicit reason the implementation would not reduce back to another global-score proxy

## Bottom line
The pair-state direction is worth keeping.
It is not yet worth reopening.

