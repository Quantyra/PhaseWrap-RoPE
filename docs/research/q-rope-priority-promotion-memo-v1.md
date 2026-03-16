# Q-RoPE Priority Promotion Memo v1

Date: 2026-03-15
Stories: S1423

## BLUF
- Q-RoPE is not a top-priority execution line yet.
- It should be promoted only if one next step can materially reduce the remaining uncertainty about realism or hardware relevance.
- Until that threshold is met, the correct posture remains `low_intensity_no_execution`.

## Current State
- The package is now stronger than the prior E003 state.
- It preserves bounded survivors across:
  - realism-bridge retrieval
  - bounded successor selection
  - bounded variable-cardinality robustness
  - bounded position-content compositionality
  - bounded content-alias disambiguation
- This is enough to preserve the line.
- It is not enough to justify concentrated scaling.

## Why The Line Is Not Top Priority Yet
- There is still no credible hardware-readiness case.
- There is still no external-claim case.
- The remaining uncertainty is about the next evidence class, not about repeating the current one harder.
- More default execution would likely increase branch count faster than decision quality.

## Promotion Threshold
Promote Q-RoPE from `low_intensity_no_execution` to a higher-priority execution posture only if at least one of the following becomes true:

1. A materially different missing-question candidate is defined whose success or failure would directly change the program's realism or hardware decision.
2. A bounded transformer-adjacent or equivalent successor evidence class is specified cleanly enough that one implementation cycle would likely resolve the next major uncertainty.
3. A concrete escalation ladder is written and accepted showing how the next bounded survivor would justify a realism or hardware screen rather than another synthetic loop.
4. A future packet produces evidence strong enough to shift the current strongest claim from selective internal relevance to a credible near-term escalation candidate.

## What Does Not Count As Promotion Evidence
- another nearby branch in an already saturated evidence class
- more transfer count
- more bridge count without a new decision layer
- package growth without a sharper escalation path

## Current Decision
- preserve the line
- keep it low intensity
- keep default execution closed
- reopen only through the missing-question gate
