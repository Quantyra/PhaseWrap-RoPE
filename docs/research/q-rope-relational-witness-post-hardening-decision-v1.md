# Q-RoPE Relational Witness Post-Hardening Decision v1

## Decision
- `BRANCH REMAINS ACTIVE`
- `DO NOT BROADEN YET`

## Why
The branch now has:
- a strong first packet
- a successful split-rotation hardening result

So the branch has crossed the bar from:
- “interesting positive”
to
- “credible active line”

## Why it still should not broaden
The strongest remaining uncertainty is feature reliance.

The witness head stayed strong under split rotation, but we still need to know:
- whether success depends on one narrow feature group
- or whether the allowed relational feature schema contributes more broadly

## Next bounded evidence step
- `feature-group ablation`

Specifically:
- remove or mask one allowed feature group at a time
- keep the same task, seeds, and split policy
- compare degradation pattern to the full witness model

## What remains disallowed
- remote execution
- benchmark expansion
- multiple new candidates

## Bottom line
The relational witness branch is now the strongest active line in the repository.
It justifies one more bounded evidence step, not broad expansion.
