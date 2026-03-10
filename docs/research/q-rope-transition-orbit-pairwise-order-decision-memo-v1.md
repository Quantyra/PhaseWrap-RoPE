# Q-RoPE Transition Orbit Pairwise Order Decision Memo v1

Date: 2026-03-11
Stories: S371-S372

## Decision
Stop the `synthetic_transition_orbit_pairwise_order_binary` execution branch.

## Why
The branch rule required witness leadership on the primary classification metrics against the fixed bounded control stack.

That did not happen:
- witness: accuracy `0.515151`, F1 `0.250000`
- strongest controls: accuracy `0.636364`, F1 `0.333333`
- lookup control: F1 `0.625000`

So the witness fails under both accuracy-first and balanced classification reading.

## Consequence
- do not widen the pairwise-order control family on this task
- do not reopen implementation on this task
- return the line to memo-only posture

## Preserved Next Angle
If this line continues, it should move to a listwise ranking task rather than another pairwise binary classifier. That is the smallest genuinely different way to test whether the witness carries ordering structure that a bounded symbolic classifier does not capture well.
