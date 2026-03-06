# Q-RoPE Post-Calibration Variant Reassessment v1

## Scope
This note reassesses the active local variant decision after the robust-calibration rerun in `S055`.

Compared evidence:
- pre-calibration larger local packet: `docs/research/q-rope-v4-vs-v3-larger-local-packet-v1.md`
- post-calibration rerun: `docs/research/q-rope-v4-robust-calibration-local-implementation-v1.md`

## Comparison
### Pre-calibration position
`V4` was retained as the active local stability track because it looked better on:
- `amazon`
- `yelp`

and only clearly worse on:
- `imdb`

That made `V4` a defensible active branch, even though it still did not justify remote promotion.

### Post-calibration position
The robust validation-based threshold rule changed the picture:
- `imdb`: `V3` and `V4` become effectively tied
- `yelp`: shifts toward `V3`
- `amazon`: shifts toward `V3`

That matters because the earlier reason to keep `V4` active was its cross-dataset local edge on `amazon` and `yelp` despite the `imdb` blocker.
After calibration, that edge no longer holds.

## Decision
### Active local reference
Return `V3` to primary local reference status.

### `V4` status
Demote `V4` from active lead branch to exploratory calibration-sensitive branch.

## Why this is the correct decision
The post-calibration evidence does not support keeping `V4` as the lead branch:
- it no longer shows a cross-dataset local advantage
- it no longer answers a high-value remote question
- the main positive signal that justified continued lead-branch status was not robust to the improved evaluation rule

This does **not** mean `V4` is discarded.
It means the burden of proof shifts back onto `V4`.

## Next zero-credit local track
Do not spend remote credits.

Run a diagnostic local track centered on score geometry rather than another variant race:
1. compare `V3` vs `V4` score distributions on the redesigned local screening backend
2. measure:
   - class-separation margin
   - calibration-threshold position relative to class score bands
   - positive-rate drift
   - per-seed score overlap
3. decide whether `V4` has a recoverable scoring geometry issue or whether it should remain exploratory until a new variant mechanism is proposed

## Remote policy implication
- no new paid `V4` wave
- no new paid `V3` wave from this decision alone
- preserve Quandela credits for a future question that is actually decision-changing

## Bottom line
The robust-calibration rerun removed the strongest argument for keeping `V4` as the active lead branch.
`V3` should now return to primary local reference status, and `V4` should continue only as an exploratory branch pending score-geometry diagnostics.
