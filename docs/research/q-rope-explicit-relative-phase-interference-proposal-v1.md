# Q-RoPE Explicit Relative-Phase Interference Proposal v1

## Purpose
Define the highest-priority future restart hypothesis as a concrete mechanism proposal.

This is still memo-level only.
It does not reopen experimentation.

## Proposed mechanism
Use an explicit relative-phase interference comparator instead of the current single-state scalar scoring path.

Target object:
- compare token-position pairs through a measured quantity that is sensitive to the relative operator
  - `P(i)^dagger P(j) = P(j - i)`

The core design idea is:
- build two branches whose interference depends on the relative phase between position-conditioned states
- measure a contrast observable that suppresses pure score-level shift and rewards offset-sensitive phase separation

## What is materially new
This is not:
- another threshold change
- another readout tweak on the same scalar score
- another overlap score with the same bottleneck

It is new because:
- the comparison primitive itself changes
- relative phase is made explicit inside the compared observable
- the measured quantity is designed to isolate offset-sensitive interference rather than aggregate activation level

## Why this addresses the observed failure mode
Observed failure in the paused line:
- `V3` often shifted the score surface upward
- but did not improve signed-offset separation

Likely reason:
- the existing path compressed phase information into a scalar that was too sensitive to global score level and too insensitive to relative-phase contrast

This proposal targets exactly that:
- replace score-level readout emphasis with interference-level contrast
- make the measurement depend on relative-phase cancellation / reinforcement rather than raw magnitude alone

## Mechanism sketch
Candidate local diagnostic form:
1. prepare a content-conditioned state for pair A
2. prepare a content-conditioned state for pair B
3. apply position-conditioned phase actions
4. combine branches in an interference-sensitive comparison step
5. measure a contrast observable whose value changes when the relative offset changes sign or magnitude

The critical requirement is:
- the measured contrast should change more with relative-offset structure than with uniform phase or amplitude shifts

## Falsifiable synthetic test
Before any broader reopening, the proposal must pass a strict synthetic test.

Use:
- the existing signed relative-offset synthetic family
- `V0` baseline
- `V_new` = explicit interference comparator path
- seeds `42`, `123`, `777`

Required pass conditions:
1. `V_new` beats `V0` on mean accuracy and mean F1, or shows a clearly dominant mechanism metric with no conflicting headline degradation
2. the signed positive-vs-negative offset gap improves over `V0`
3. the score-vs-offset curve becomes more structured under `V_new`
4. the effect is not explained by a uniform score shift

Fail conditions:
- mixed headline metrics with no mechanism win
- higher overall score level but unchanged separation
- seed-fragile improvement only

## Required observable
Any future implementation must name the observable before code work starts.

Minimum acceptable observable property:
- it must distinguish relative-phase contrast from global score elevation

If the observable cannot do that on paper, the proposal should not be implemented.

## Why this is better than the stopped pairwise-overlap branch
The earlier pairwise-overlap branch failed because it collapsed `V0` and `V3` into nearly identical behavior.

This proposal differs by requiring:
- explicit interference contrast
- not just similarity magnitude
- and an observable selected for phase-sensitive discrimination

So this is materially different from the stopped branch.

## Risks
- the comparator may still collapse into an offset-insensitive signal
- the observable may remain too compressive
- the synthetic gate may fail quickly

These are acceptable risks because the falsification path is cheap and explicit.

## Restart standard
Do not reopen coding unless the future proposal work answers:
1. exact state-preparation structure
2. exact comparison/interference step
3. exact observable
4. exact synthetic falsification packet

## Bottom line
If Quantyra reopens this initiative, the strongest next mechanism proposal is:
- `explicit relative-phase interference comparison`

It is the best candidate because it directly targets the known failure mode:
- phase was present,
- but the measurement path did not turn it into useful relative-offset separation.
