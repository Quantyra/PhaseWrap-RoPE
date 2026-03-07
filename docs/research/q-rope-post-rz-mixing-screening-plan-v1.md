# Q-RoPE Post-RZ Mixing Screening Plan v1

## Decision
Screen stronger post-`RZ` mixing on the primary `V3` path as a zero-credit local mechanism study.

This is:
- local mechanism screening
- infrastructure and signal-formation work

This is not:
- a new algorithm branch
- a new Q-RoPE novelty claim
- a remote-execution question

## Why this is the right scope
Current evidence shows:
- the first meaningful variant-sensitive divergence appears after the global `RX` mixing stage
- parity is now the strongest local screening readout
- the unresolved bottleneck is post-phase conversion, not thresholding and not readout selection alone

So the right next step is to perturb the mixing path directly while keeping everything else fixed.

## Screening question
Does stronger or richer post-`RZ` mixing on `V3` produce better local class separation and decision quality under parity readout?

## Minimal candidate set
Keep the candidate set narrow:
1. `mix_v0`
   - current baseline
   - single global `RX(pi/4)`
2. `mix_v1`
   - stronger global mixing
   - e.g. larger fixed `RX` angle
3. `mix_v2`
   - two-stage mixing
   - e.g. `RX` layer, entangling, second `RX` layer

Do not expand beyond these until one of them shows a clear local signal.

## Fixed controls
Keep fixed:
- variant: `V3`
- default readout: `parity`
- weighted shadow only if the result materially affects branch conclusions
- datasets: `yelp`, `imdb`, `amazon`
- seeds: `42`, `123`, `777`, `2024`, `9001`

## Local evaluation packet
Primary packet:
- backend: `sim_quantum_statevector`
- variant: `V3`
- readout: `parity`
- compare `mix_v0`, `mix_v1`, `mix_v2`

Secondary shadow packet:
- weighted only if one mixing choice appears strong enough to affect a later branch decision

## Decision criteria
A mixing alternative is worth carrying forward only if it improves:
1. class separation or F1 on at least two datasets
2. stability across seeds
3. worst-seed behavior

If it only improves one dataset or only improves variance while collapsing mean performance, it is not enough.

## Output framing
Any positive result from this step must be framed as:
- local mechanism-screening evidence

Not as:
- a new algorithm
- a remote-readiness signal

## Recommended next story
Implement configurable local mixing presets in the simulator path and run the zero-credit screening packet.

## Bottom line
The next correct move is a narrow post-`RZ` mixing screen on `V3` under parity readout.
That is the highest-value unresolved local mechanism question.
