# Q-RoPE Alternative Observable Screening Plan v1

## Decision
This is a **local screening-path redesign question**, not a new-variant question.

## Why
Current evidence says:
- weighted mean excitation is too compressive
- alternative observables can increase dynamic range
- but richer observables alone do not create strong class separation

So the next high-value question is not:
- "what is the next variant?"

It is:
- "can the local screening path be made more decision-useful with a better observable?"

## Candidate observables to screen
Limit the screening wave to:
1. `q2`
2. `parity`

Why these two:
- both materially increase score spread relative to weighted mean excitation
- both are easy to compute from the same final state
- they represent two distinct readout families:
  - local single-qubit excitation
  - global parity-style population structure

Do **not** prioritize:
- `weighted`
  - known compression bottleneck
- `q0`
  - modest gain, not enough signal
- `q1`
  - intermediate but less compelling than `q2`
- `topheavy`
  - richer than weighted, but not as informative as `q2` or `parity`

## Zero-credit screening packet
Backend:
- `sim_quantum_statevector`

Variants:
- `V3` primary reference
- `V4` exploratory comparator

Datasets:
- `yelp`
- `imdb`
- `amazon`

Seeds:
- `42`
- `123`
- `777`
- `2024`
- `9001`

Readouts to compare:
- current `weighted`
- candidate `q2`
- candidate `parity`

## Decision criteria
An alternative observable is worth carrying forward only if it improves all three:
1. score spread or range
2. class separation or overlap behavior
3. stability across seeds

If it improves only spread without improving decision quality, it is not enough.

## What success would mean
Success does **not** mean remote promotion.

Success means:
- the local screening path becomes more discriminative
- future local variant decisions become less noisy
- a later mechanism-level branch would be evaluated on a better local gate

## What failure would mean
If `q2` and `parity` both fail to improve decision usefulness enough, then:
- the local screening path itself needs a deeper redesign
- opening a new variant branch before that would be premature

## Bottom line
The next protocol step should screen `q2` and `parity` as local observable upgrades.
That is a local infrastructure decision, not a new-variant decision.
