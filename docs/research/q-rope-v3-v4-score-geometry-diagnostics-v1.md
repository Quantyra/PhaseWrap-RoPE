# Q-RoPE V3 vs V4 Score-Geometry Diagnostics v1

## Scope
This note analyzes score-level geometry for `V3` and `V4` on the deterministic local screening backend after the post-calibration reassessment.

Backend:
- `sim_quantum_statevector`

Credit status:
- `0` additional Quandela credits consumed

Diagnostic artifact:
- `logs/diagnostics/v3_v4_score_geometry.json`

## Packet
- variants: `V3`, `V4`
- datasets: `yelp`, `imdb`, `amazon`
- seeds: `42`, `123`, `777`, `2024`, `9001`

Metrics extracted:
- class-separation margin: `mean(score_pos) - mean(score_neg)`
- score-band gap: `min(score_pos) - max(score_neg)`
- threshold offset from midpoint of the class means
- predicted-positive-rate drift from the test-set class prior
- overlap rate at the calibrated threshold

## Aggregate result
### Yelp
- `V3`: mean margin `0.0157`, mean band gap `-0.1509`, mean threshold offset `0.0420`, mean drift `0.2250`, mean overlap `0.3750`
- `V4`: mean margin `0.0169`, mean band gap `-0.1371`, mean threshold offset `0.0277`, mean drift `0.2250`, mean overlap `0.4250`

Interpretation:
- `V4` slightly improves raw separation geometry
- `V4` does not improve rate drift
- `V4` worsens overlap at the decision threshold

### IMDb
- `V3`: mean margin `0.0180`, mean band gap `-0.1042`, mean threshold offset `0.0380`, mean drift `0.2750`, mean overlap `0.4750`
- `V4`: mean margin `0.0154`, mean band gap `-0.0824`, mean threshold offset `0.0281`, mean drift `0.2750`, mean overlap `0.4750`

Interpretation:
- `V4` slightly weakens average class-mean separation
- `V4` slightly improves the worst-band geometry
- the decision-level behavior remains unchanged because overlap and rate drift do not improve

### Amazon
- `V3`: mean margin `-0.0100`, mean band gap `-0.1248`, mean threshold offset `-0.0255`, mean drift `0.3000`, mean overlap `0.4500`
- `V4`: mean margin `-0.0049`, mean band gap `-0.0972`, mean threshold offset `-0.0188`, mean drift `0.3500`, mean overlap `0.5000`

Interpretation:
- `V4` improves raw score geometry somewhat
- `V4` worsens threshold behavior
- `V4` increases both rate drift and overlap

## Seed-level pattern
The consistent pattern is:
- `V4` can improve raw separation metrics on some seeds
- those gains are not stable across seeds
- when raw separation improves, it often fails to reduce overlap
- in the worst cases, `V4` increases positive-rate drift while leaving the classification boundary no cleaner

This means the current issue is not simply:
- too much threshold bias
- or too little raw separation

It is a deeper mismatch between the score geometry produced by `V4` and the downstream decision surface.

## Decision framework outcome
### Is `V4` recoverable with more local calibration work alone?
Current answer: `No clear evidence`

Why:
- the post-calibration rerun already removed the easiest calibration artifact
- geometry gains from `V4` do not reliably translate into reduced overlap
- no dataset shows a clean combination of:
  - better margin
  - better overlap
  - lower drift

### Should `V4` remain worth local refinement?
Current answer: `Only as a bounded exploratory branch`

That means:
- do not promote `V4`
- do not spend remote credits on `V4`
- do not keep iterating thresholds as if the problem were purely calibration

## Recommended next local track
The next zero-credit track should target score formation rather than thresholding:
1. inspect whether `V4` changes the score range too weakly or too uniformly across tokens
2. compare token-to-score sensitivity between `V3` and `V4`
3. determine whether a future variant needs a different phase-to-score coupling mechanism rather than another threshold rule

## Bottom line
`V4` does not currently show a recoverable advantage through score geometry alone.
It should remain exploratory until there is a new mechanism-level reason to revisit it.
