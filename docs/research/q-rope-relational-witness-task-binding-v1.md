# Q-RoPE Relational Witness Task Binding v1

## Decision
- bind the witness-head path to one task only:
  - `synthetic_sector_parity_binary`

## Why this task
It is already the strongest alignment-safe synthetic family in the archive:
- relational
- sector-based
- not reducible to offset sign alone

That makes it the right first falsification task for a witness-head restart.

## Why no second task now
Adding more tasks at this stage would weaken causal clarity.

The witness-head angle needs one sharp test first:
- do constrained sector-first quantum features become useful when the final decision rule is slightly relaxed?

That question does not require multiple tasks yet.

## Fixed first packet
- baseline: `V0`
- candidate: one future witness-head branch only
- seeds: `42`, `123`, `777`
- local-only
- synthetic-only

## Interpretation rule
If the witness-head branch fails here, the correct read is:
- the quantum sector-response features were not enough even under a tiny explicit head

That would close this angle cleanly.

## Bottom line
The witness-head path is now tied to one exact falsification task and no others.
