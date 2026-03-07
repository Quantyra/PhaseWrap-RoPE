# Q-RoPE Future Restart Brief Template v1

Use this template only if Quantyra decides to propose a future restart.

Submitting this brief does not authorize implementation.
It is a gate document.

## 1. Restart title
- brief title:
- date:
- owner:

## 2. Mechanism hypothesis
- What is the new mechanism?
- What is materially different from the paused implementation line?
- Why is this not just another threshold, readout, or local-tuning tweak?

## 3. Failure mode targeted
- Which observed failure mode from the paused line does this address?
- Why should this mechanism improve relative-offset separation instead of merely shifting scores upward?

## 4. Exact state-preparation structure
- branch/state A:
- branch/state B:
- where token content enters:
- where positional phase enters:
- what remains separable and interpretable before comparison:

## 5. Exact interference/comparison structure
- comparison primitive:
- where relative operator `P(i)^dagger P(j)` is exposed:
- why this comparator is phase-sensitive:
- why this is not equivalent to the previously stopped pairwise-overlap branch:

## 6. Exact observable
- observable definition:
- why it distinguishes relative-phase contrast from global score elevation:
- what outcome would count as evidence the observable is working:

## 7. Synthetic falsification packet
- dataset:
- seeds:
- baseline:
- proposed variant:
- readout policy:
- no-remote confirmation:

Default expected packet:
- dataset: `synthetic_offset_binary`
- seeds: `42`, `123`, `777`
- baseline: `V0`
- candidate: `V_new`
- backend: `sim_quantum_statevector`
- remote execution: `disallowed`

## 8. Predeclared success criteria
The proposal must state in advance:
- required mean accuracy condition:
- required mean F1 condition:
- required score-vs-offset improvement:
- required positive-minus-negative offset-gap improvement:
- required evidence that the result is not a uniform score shift:

## 9. Predeclared failure criteria
Implementation must stop if any of these occur:
- mixed headline metrics with no mechanism win
- no score-vs-offset structure gain
- no offset-gap improvement
- effect explainable by uniform score elevation
- one-seed-only improvement

## 10. Minimal implementation boundary
- exact files expected to change:
- exact files not allowed to change:
- tests required before first run:
- diagnostics required per run:

## 11. Budget and scope guardrails
- Quandela credits allowed: `0`
- IBM remote allowed: `no`
- broad benchmark expansion allowed: `no`
- new variant branching allowed: `only if named in this brief`

## 12. Decision request
- Why should Quantyra approve implementation of this restart proposal?
- What is the smallest decisive experiment?
- What result would make us stop immediately?

## Approval rule
Do not implement unless this brief is complete and explicitly approved as a new restart phase.
