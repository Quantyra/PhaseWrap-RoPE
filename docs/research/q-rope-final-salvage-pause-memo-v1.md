# Q-RoPE Final Salvage Pause Memo v1

## Status
Set the initiative to:
- `paused`
- `internal archive`
- `publication gated off`

This is the correct disposition under the current evidence.

## Why the initiative is paused
The project was given a fair salvage path:
- controlled synthetic theorem-to-mechanism validation
- zero-credit local execution
- explicit `V0` vs `V3` comparison
- final score-vs-offset diagnostics

That salvage path did not produce a positive result.

The decisive observation is:
- `V3` raised the overall score surface
- but did not improve signed relative-offset separation over `V0`

So the current implementation line does not justify:
- more synthetic expansion
- more local tuning
- more remote spend
- any publication push

## Why quantum phase did not automatically help
The failure is not evidence that RoPE-like ideas are mathematically incoherent in quantum settings.
It is evidence that complex amplitudes alone are not enough.

What likely happened:
1. quantum phase existed in the state, but
2. the comparison and readout path did not convert that phase into stronger relative-offset discrimination, and
3. the current mechanism mostly produced a score-level shift rather than a cleaner offset-sensitive geometry

In other words:
- quantum provides the representational ingredients
- it does not automatically provide the useful observable geometry

That is the main lesson from this repo.

## Restart conditions
Do not reopen the initiative unless all of the following are satisfied.

### Condition 1
A materially new mechanism hypothesis exists.

Examples of acceptable restart hypotheses:
- a new query-key comparison primitive that explicitly targets `P(i)^dagger P(j)` structure
- a new observable/readout family with a reasoned mechanism for turning phase into offset-sensitive separation
- a new architecture-level comparison path that is not just another local tuning variant

Non-acceptable restart hypotheses:
- more threshold tuning
- another small local tail tweak
- more cloud runs on the same mechanism
- reopening `V4` or `V4b` as they currently stand

### Condition 2
The new mechanism passes a synthetic theorem test first.

Required standard:
- `V_new` must beat `V0` on a controlled relative-offset synthetic family
- the result must hold across multiple seeds
- the win must be visible in mechanism diagnostics, not just a single headline metric

### Condition 3
Diagnostics must show real offset structure.

Required standard:
- score-vs-offset curves must show clearer relative-offset separation than the baseline
- the result must not be explained by a uniform score shift alone
- the effect must survive leakage checks

### Condition 4
Only after the synthetic gate clears may benchmark or hardware work reopen.

That means:
- no new IBM or Quandela spend before a synthetic win
- no broader benchmark expansion before a synthetic win
- no publication or external framing before a synthetic win

## Allowed work while paused
- repo hygiene
- internal archival summaries
- evidence preservation
- future restart design work at memo level

## Disallowed work while paused
- new experiment waves under the current mechanism line
- remote comparator expansion
- public positioning
- publication packaging

## Bottom line
The project is not deleted.
It is paused with explicit restart conditions.

A restart is justified only if Quantyra has a materially new mechanism hypothesis and that hypothesis wins on controlled synthetic theorem-validation before any broader reopening.
