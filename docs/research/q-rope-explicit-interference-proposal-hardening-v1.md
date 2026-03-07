# Q-RoPE Explicit Interference Proposal Hardening v1

## Purpose
Raise the top-ranked restart proposal from concept level to implementation-ready memo level.

This still does not authorize coding.

## Exact proposal standard
Any future implementation proposal must specify all four of these elements before code work starts:
1. state-preparation structure
2. interference/comparison structure
3. observable
4. synthetic falsification packet

If any one of these is missing, the proposal is incomplete and the repo stays paused.

## Proposed state-preparation structure
Use two explicitly compared branches:
- branch `A`: token-position pair `(x_i, i)`
- branch `B`: token-position pair `(x_j, j)`

Per branch:
- prepare content-conditioned state `E(x)`
- apply position-conditioned phase family `P(i)` or `P(j)`

Minimal target form:
- `|psi_i> = P(i) E(x_i) |0>`
- `|psi_j> = P(j) E(x_j) |0>`

Required property:
- content and position remain interpretable as separate components before comparison

## Proposed interference/comparison structure
The comparator must explicitly expose relative phase, not just similarity magnitude.

Minimum acceptable comparison idea:
- build a contrast quantity from the superposition or interference between `|psi_i>` and `|psi_j>`
- the sign or magnitude of that contrast should depend on the relative operator
  - `P(i)^dagger P(j)`

Rejected comparison forms:
- plain scalar score on one branch only
- plain overlap magnitude with no explicit phase-sensitive contrast argument

## Proposed observable requirement
The observable must separate:
- global score elevation
from
- relative-phase-sensitive contrast

Minimum acceptable observable statement:
- explain why a uniform score shift would not produce the same diagnostic effect as a true relative-offset phase effect

This is the protection against repeating the last failure mode.

## Minimum falsification packet
The first implementation must be falsified on the smallest decisive packet:
- dataset: `synthetic_offset_binary`
- seeds: `42`, `123`, `777`
- variants:
  - `V0`
  - `V_new`
- no remote execution
- no benchmark expansion

Required outputs:
- accuracy
- F1
- score-vs-offset curve
- positive-minus-negative offset separation
- overall score-level shift metric

## Restart success criteria
To justify a real restart, the proposal must declare in advance that `V_new` passes only if:
1. it beats `V0` on mean accuracy and mean F1, or produces a clearly superior mechanism metric with no contradictory degradation
2. its score-vs-offset curve shows clearer signed-offset structure than `V0`
3. its positive-minus-negative offset gap improves over `V0`
4. its effect is not explained by uniform elevation alone

## Restart failure criteria
The proposal must also declare in advance that implementation stops if:
- the metric story is mixed again
- the mechanism metric does not improve
- the curve shape remains weak or ambiguous
- the effect can still be explained as a score-surface shift

## Why this hardening matters
Without this bar, the repo will drift back into:
- partial ideas
- under-specified experiments
- ambiguous post hoc interpretation

This memo prevents that.

## Recommendation
Do not move to implementation from this repo state unless a future proposal document can instantiate all four required elements above with enough precision that the falsification packet is fixed before coding begins.

## Bottom line
The explicit interference comparator remains the best future restart candidate.
But it is still only a candidate until someone writes the exact comparator and observable in a falsifiable form.
