# Q-RoPE Relational Witness Decision Memo v1

## Decision
- `PROVISIONAL GO`
- `DO NOT BROADEN YET`

## Why
The first packet cleared the approved gate:
- better mean accuracy than `V0`
- better mean F1 than `V0`
- multi-seed consistency
- anti-collapse preserved
- forbidden inputs absent

That is enough to keep the branch alive.

## Why this is still only provisional
It is still only one bounded packet.

The right next move is not:
- broader benchmarks
- remote execution
- more variants

The right next move is:
- one validity-hardening step

## What must be hardened
The strongest remaining question is whether the witness head is using the intended relational evidence robustly, not merely exploiting one convenient feature combination under the current split.

So the next step should stress:
- split robustness
- coefficient stability
- feature reliance pattern

## Current branch posture
- active
- still local-only
- still synthetic-only
- still one-candidate only

## Bottom line
This is the strongest positive result in the repository so far.
It justifies one more disciplined hardening step, not expansion.
