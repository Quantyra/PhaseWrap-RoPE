# Q-RoPE Synthetic Falsification Packet v1

## Decision
Bind the future explicit-interference mechanism to one fixed falsification packet before any implementation is authorized.

## Fixed packet
- dataset: `synthetic_offset_binary`
- backend: `sim_quantum_statevector`
- seeds:
  - `42`
  - `123`
  - `777`
- baseline:
  - `V0`
- candidate:
  - `V_new_explicit_interference`
- remote execution:
  - `disallowed`
- benchmark expansion:
  - `disallowed`

## Fixed mechanism assumptions
This packet assumes:
- branch structure from [q-rope-state-preparation-design-v1.md](\\?\C:\Users\Dan\Desktop\Projects\QuantyraQRope\docs\research\q-rope-state-preparation-design-v1.md)
- comparator from [q-rope-comparator-interference-design-v1.md](\\?\C:\Users\Dan\Desktop\Projects\QuantyraQRope\docs\research\q-rope-comparator-interference-design-v1.md)
- observable from [q-rope-observable-readout-design-v1.md](\\?\C:\Users\Dan\Desktop\Projects\QuantyraQRope\docs\research\q-rope-observable-readout-design-v1.md)

No future implementation proposal may silently substitute different defaults.

## Required outputs
For both `V0` and `V_new_explicit_interference`, record:
- test accuracy
- test F1
- score-vs-offset curve
- positive-minus-negative offset gap
- overall score-level shift metric
- per-seed breakdown

## Predeclared success rule
Implementation is `GO` only if all are met:
1. `V_new_explicit_interference` beats `V0` on mean accuracy across the packet
2. `V_new_explicit_interference` beats `V0` on mean F1 across the packet
3. score-vs-offset structure is clearer than `V0`
4. positive-minus-negative offset gap is larger than `V0`
5. the effect cannot be explained by overall score elevation alone
6. the signal is present in at least two of the three seeds

## Predeclared failure rule
Implementation is `STOP` immediately if any are true:
1. mean accuracy loses to `V0`
2. mean F1 loses to `V0`
3. score-vs-offset curve is not cleaner than `V0`
4. positive-minus-negative offset gap does not improve
5. the main effect is still a uniform score shift
6. any gain appears in only one seed

## Why the rule is this strict
The paused line already produced:
- mixed metrics
- unstable seed behavior
- score-surface shifts without mechanism win

So the restart bar has to be higher than “some metrics moved.”

## Shadow reference policy
If a future implementation argues that parity contrast is winning only because of readout choice, it may include:
- one shadow readout comparison

But:
- the shadow comparison cannot replace the primary packet
- it cannot weaken the pass/fail rule

## Minimal implementation boundary for the future
If implementation is ever approved, the first code phase must stay minimal:
- new comparator path
- new observable path
- synthetic packet only

No additional changes:
- no new datasets
- no cloud hooks
- no new benchmark family

## Bottom line
The future mechanism now has a fixed falsification packet.
If it cannot clear this packet cleanly, the restart should fail fast and stop again.
