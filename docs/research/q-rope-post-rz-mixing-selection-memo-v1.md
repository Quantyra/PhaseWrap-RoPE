# Q-RoPE Post-RZ Mixing Selection Memo v1

## Decision
Decision: `STOP` the current fixed post-`RZ` mixing preset branch as an active mechanism-improvement track.

Retain:
- `mix_v0` as the local baseline

Do not promote:
- `mix_v1`
- `mix_v2`

## Why
The completed screen answered the branch question with enough evidence.

### `mix_v1`
- helps `imdb`
- does not improve `yelp`
- regresses `amazon`

Conclusion:
- too narrow
- not a viable general local upgrade

### `mix_v2`
Under parity:
- helps `yelp`
- helps `amazon`
- regresses `imdb`

Under weighted shadow:
- regresses `yelp`
- regresses `amazon`
- helps `imdb`

Conclusion:
- effect is readout-dependent
- effect is dataset-dependent
- not stable enough for branch promotion

## Interpretation
This branch was worth running because it resolved a real mechanism question:
- modest fixed post-`RZ` mixing changes do alter the local signal

But it also showed the limit of this line:
- the current bottleneck is not solvable by a small fixed mixing tweak alone

That means the next step should not be:
- more preset tuning
- more local threshold tuning
- remote spend

The next step should be:
- a broader local circuit/readout redesign question

## Protocol consequence
Primary local mechanism path remains:
- `V3`
- `parity` default local screening readout
- `weighted` shadow when policy requires it
- baseline mixing `mix_v0`

Closed branch:
- fixed post-`RZ` mixing preset exploration

## Recommended next question
If the goal is to improve local discriminative power further, the next defensible question is:

Can a broader local circuit/readout redesign improve state separability more reliably than fixed post-`RZ` mixing tweaks?

## Bottom line
The branch is no longer worth active iteration.
The result is informative but negative:
- keep `mix_v0`
- stop preset tuning
- move to the next broader zero-credit local redesign question
