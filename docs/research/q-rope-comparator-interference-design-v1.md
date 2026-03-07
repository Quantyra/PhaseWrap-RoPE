# Q-RoPE Comparator/Interference Design v1

## Decision
Use an interference-contrast comparator, not a plain similarity-magnitude comparator.

Proposed comparator target:
- compare branch `A` and branch `B` through the contrast between constructive and destructive interference channels

## Comparator definition
Given:
- `|psi_i> = P(i) E(x_i) |0>`
- `|psi_j> = P(j) E(x_j) |0>`

Define two comparison channels conceptually:
- constructive channel proportional to `|psi_i> + |psi_j>`
- destructive channel proportional to `|psi_i> - |psi_j>`

The future measured quantity should be a contrast between these channels, not just the norm or overlap of one channel alone.

Minimum target form:
- `C(i,j) := M_plus(i,j) - M_minus(i,j)`

Where:
- `M_plus` is an observable response on the constructive branch
- `M_minus` is an observable response on the destructive branch

## Why this is materially different from the stopped pairwise-overlap line
The stopped pairwise-overlap branch effectively reduced comparison to similarity magnitude.

That was insufficient because:
- it could not distinguish useful relative-phase contrast from generic closeness
- it collapsed `V0` and `V3` into nearly identical behavior

This comparator is different because:
- it explicitly uses **two** interference channels
- it measures **contrast**, not just similarity magnitude
- destructive interference gives a route for relative-phase mismatch to appear directly in the observable

So the new target is:
- not “how close are the states?”
- but “how much does constructive-versus-destructive channel behavior change with relative offset?”

## Why this targets the observed failure mode
Observed failure:
- the previous implementation often produced a uniform score shift

Why this comparator is better matched:
- a uniform score elevation should affect both channels more symmetrically
- a genuine relative-phase effect should alter the constructive/destructive balance

That is the specific discrimination property we need.

## Relative-phase link
This design is aligned to the theorem target because:
- the compared object is not a single branch score
- the branch interaction should depend on the phase relation between `P(i)` and `P(j)`
- that relation is where `P(i)^dagger P(j)` enters

The comparator therefore has a direct route for relative-offset structure to matter.

## Comparator requirements
Any future implementation must preserve these constraints:
1. both channels are derived from the same branch states
2. constructive and destructive channels are both observable
3. the reported score is a contrast between them
4. the contrast cannot be reduced to plain overlap magnitude

## Why this is still only a proposal
This memo does **not** define the observable yet.

That is intentional.
The comparator here defines:
- what interaction to expose

The next story must define:
- how to observe it

## Failure conditions for this comparator idea
This comparator should be rejected before implementation if:
- the eventual observable would collapse `M_plus - M_minus` into a monotone transform of similarity magnitude
- the constructive/destructive distinction cannot be preserved in the chosen measurement path
- the design still cannot explain why relative-offset structure, not score shift, should dominate

## Bottom line
The new comparison primitive should be an interference contrast:
- constructive channel vs destructive channel

That is the clearest way to make the next restart genuinely different from the failed pairwise-overlap path.
