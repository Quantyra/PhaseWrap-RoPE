# Q-RoPE V4 Robust Local Calibration Protocol v1

## Decision
Do **not** start `V5` yet.

## Why not `V5` yet
The current blocker is still evaluation stability, not exhausted variant design space.

What we know:
- `V4` remains the best active local branch
- `V4` survives the larger local packet on `amazon` and `yelp`
- `imdb` remains the blocker
- the `imdb` issue appears calibration-linked, not clearly structural

Starting `V5` now would lower discipline:
- it would add a new algorithm branch before we have stabilized the evaluation protocol
- it would make it harder to tell whether future gains come from a better model or a better decision rule
- it would increase branching without answering the current highest-value question

## Preferred protocol
Use a robust local calibration protocol for `V4` first.

Recommended protocol:
1. split train into:
   - subtrain
   - validation
2. fit threshold on validation, not on full train mean
3. select threshold with a balanced objective:
   - primary: macro-F1 or balanced accuracy
   - secondary tie-break: lower positive-rate drift from the validation label prior
4. freeze that rule across all local packets before reevaluating remote questions

## Why this protocol
The prior sweep showed:
- train mean is too brittle
- train median recovers some performance but inflates variance
- balanced-train can collapse F1
- naive validation-split can recover mean metrics but still be unstable

So the next step is not “pick the best ad hoc threshold.”
It is to define one robust calibration rule and apply it consistently.

## When `V5` would become justified
Start `V5` only if one of these becomes true:
1. `V4` still fails after robust calibration protocol is applied consistently
2. the remaining blocker looks structural rather than calibration-linked
3. there is a concrete new mechanism to test that is not just another scale tweak

## Active recommendation
- active local branch: `V4`
- immediate next step: robust calibration protocol
- `V5`: deferred

## Bottom line
The technically correct move is to harden the local evaluation protocol around `V4`.
`V5` is premature right now.
