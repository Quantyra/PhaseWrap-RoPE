# Q-RoPE Restart Hypothesis Scouting v1

## Purpose
Define what a valid future restart would look like after the pause.

This is memo-level work only.
It does not reopen experimentation.

## Why a new mechanism is still possible
The current line failed because the implemented mechanism did not turn phase into stronger relative-offset discrimination.

That is not the same as proving the broader idea is impossible.

The core distinction is:
- `phase exists in the representation`
vs
- `phase is converted into a useful observable comparison geometry`

The repo showed the first without proving the second.

## Ranked restart candidates

### Candidate 1
`Explicit relative-phase interference comparator`

Concept:
- build a comparison primitive that directly contrasts `P(i)^dagger P(j)` against a content-only baseline inside the measured observable
- avoid single-state scalar scoring
- avoid uniform score-surface shifts by construction

Why this ranks first:
- it attacks the exact failure mode we observed
- it is closest to the theorem target
- it gives the clearest synthetic theorem-validation path

What would make it materially new:
- a new observable or interference construction that explicitly isolates relative-phase contribution
- not just another overlap score with the same readout bottleneck

### Candidate 2
`Observable family redesign for phase-sensitive separation`

Concept:
- keep the positional idea largely intact
- redesign the measurement family so phase differences produce stronger signed-offset separation

Why this ranks second:
- our diagnostics repeatedly showed the readout/comparison path was the bottleneck
- this is still a mechanism change, not just calibration

Why it is not first:
- by itself it risks becoming another local-tuning loop
- it only deserves reopening if the new observable has a concrete mechanism argument

### Candidate 3
`Architecture-level query-key path redesign`

Concept:
- move closer to an actual hybrid quantum attention comparison path instead of the current proxy scoring route

Why this has merit:
- classical RoPE’s usefulness is tied to query-key geometry, not phase alone

Why it ranks third:
- it is more expensive
- harder to diagnose causally
- easier to drift back into benchmark sprawl before proving mechanism value

## Non-candidates
Do not reopen under these labels:
- `V4`
- `V4b`
- threshold recalibration
- small mixing-preset changes
- more remote expansion on the same mechanism

These were already tested enough to stop.

## Minimum restart proposal standard
Any future restart proposal must answer all of these before code work resumes:
1. What is materially new about the mechanism?
2. Why should it improve relative-offset separation rather than merely shift scores?
3. What synthetic theorem-test will falsify it quickly?
4. What observable proves the mechanism worked?

If a proposal cannot answer those, it is not restart-worthy.

## Recommended next memo if Quantyra wants to reopen later
Write one focused proposal for Candidate 1 only:
- explicit relative-phase interference comparator

That is the best next restart hypothesis because it addresses the exact failure mode we observed and stays close to the original theorem target.

## Bottom line
Yes, a new mechanism is still possible.
But the next restart must begin as a new mechanism proposal, not as a continuation of the failed implementation line.
