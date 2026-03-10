# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Margin Decision Memo v1

Date: 2026-03-10
Status: stopped
Story: S516

## Decision
- stop the execution branch

## Reason
- the witness led the fixed control stack on `mae`
- the witness failed the second declared primary metric, `rank_correlation`
- two bounded symbolic controls retained materially positive rank structure while the witness was effectively flat to slightly negative
- under the approved two-metric gate, mixed leadership is not enough

## Consequence
- do not widen this branch
- do not add hardening on this branch
- preserve only a memo-level next angle
