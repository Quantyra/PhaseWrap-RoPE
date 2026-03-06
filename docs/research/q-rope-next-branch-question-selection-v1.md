# Q-RoPE Next Branch Question Selection v1

## Decision
The next highest-value zero-credit branch question is:

**Can the local screening path gain discriminative power by strengthening phase-to-amplitude conversion on the primary `V3` path, before opening any new variant branch?**

## Why this is the right next question
The current evidence stack says:
- `V4` is exploratory only
- parity is now the strongest local screening readout
- weighted remains a shadow reference for important decisions
- the main unresolved bottleneck is still post-phase signal conversion, not thresholding

That means the next question should target:
- mechanism-level signal formation

Not:
- more readout tuning
- another `V4` rescue attempt
- remote execution

## Why this question beats the alternatives
### Not `V4` again
`V4` has already failed the burden-of-proof test repeatedly:
- score compression
- weak token sensitivity
- no robust cross-dataset edge

### Not `V5` yet
A new branch is still premature until we know whether the current local path can be improved by a cleaner post-phase coupling mechanism.

### Not remote execution
No local evidence currently justifies spending credits on a new remote question.

## Concrete form of the question
Stay on `V3` as the primary local reference and ask:
1. does a stronger or richer post-`RZ` mixing path produce better class separation under parity readout?
2. if yes, is that improvement strong enough to justify a new mechanism-level branch later?

This keeps the question infrastructure-grounded and avoids premature novelty inflation.

## Next local story class
The next story should be a local mechanism-screening plan, centered on:
- post-phase mixing alternatives
- parity as default readout
- weighted as shadow only if the result affects branch status

## Policy alignment
This selection is aligned with the current policy:
- parity default
- weighted shadow only for important decisions
- zero-credit local path only
- no remote reopening

## Bottom line
The next branch question should focus on improving phase-to-amplitude conversion on the primary local reference path.
That is the highest-value unresolved local question now.
