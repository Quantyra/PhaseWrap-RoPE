# Q-RoPE Filled Restart Brief v1

Submitting this brief does not authorize implementation.
It is a decision document for a future restart phase.

## 1. Restart title
- brief title: `V_new_explicit_interference`
- date: `2026-03-07`
- owner: `Quantyra Research`

## 2. Mechanism hypothesis
- New mechanism:
  - explicit relative-phase interference comparison using constructive-versus-destructive branch contrast
- Material difference from the paused line:
  - replaces single-state scalar scoring and stopped similarity-magnitude comparison with a two-channel interference contrast
- Why this is not another tweak:
  - it changes the comparison primitive itself
  - it changes the observable itself
  - it is not a threshold, calibration, readout-only, or small-circuit-tuning proposal

## 3. Failure mode targeted
- Targeted failure mode:
  - prior mechanisms preserved phase but mostly produced uniform score shifts instead of stronger relative-offset separation
- Why this should improve relative-offset separation:
  - the comparator is built around constructive-versus-destructive balance
  - a true relative-phase effect should perturb that balance
  - a uniform score elevation should affect both channels more symmetrically and therefore be less likely to mimic success

## 4. Exact state-preparation structure
- branch/state A:
  - `|psi_i> = P(i) E(x_i) |0^q>`
- branch/state B:
  - `|psi_j> = P(j) E(x_j) |0^q>`
- where token content enters:
  - through the shared deterministic content loader `E(x)`
- where positional phase enters:
  - through branch-local commuting phase family `P(i)` / `P(j)` applied after content loading
- what remains separable and interpretable before comparison:
  - token identity on each branch
  - position index on each branch
  - shared content-loader structure
  - shared phase-family structure

## 5. Exact interference/comparison structure
- comparison primitive:
  - constructive-versus-destructive channel contrast
- where relative operator `P(i)^dagger P(j)` is exposed:
  - in the interaction between branch `A` and branch `B` when comparing the constructive channel `|psi_i> + |psi_j>` against the destructive channel `|psi_i> - |psi_j>`
- why this comparator is phase-sensitive:
  - phase alignment and phase mismatch should rebalance constructive and destructive responses differently
- why this is not equivalent to the previously stopped pairwise-overlap branch:
  - the stopped branch reduced comparison to similarity magnitude
  - this proposal measures channel contrast, not closeness alone

## 6. Exact observable
- observable definition:
  - `O(i,j) = Parity_plus(i,j) - Parity_minus(i,j)`
- why it distinguishes relative-phase contrast from global score elevation:
  - a global elevation should shift both channel readouts more symmetrically
  - a true relative-phase effect should change the constructive/destructive parity balance
- what outcome would count as evidence the observable is working:
  - larger signed-offset separation under `V_new_explicit_interference`
  - cleaner score-vs-offset structure
  - effect not explainable by overall score-level increase alone

## 7. Synthetic falsification packet
- dataset:
  - `synthetic_offset_binary`
- seeds:
  - `42`, `123`, `777`
- baseline:
  - `V0`
- proposed variant:
  - `V_new_explicit_interference`
- readout policy:
  - primary = parity contrast
  - optional shadow readout only if needed to rule out readout artifact
- no-remote confirmation:
  - yes

## 8. Predeclared success criteria
- required mean accuracy condition:
  - `V_new_explicit_interference` must beat `V0` on mean accuracy across the packet
- required mean F1 condition:
  - `V_new_explicit_interference` must beat `V0` on mean F1 across the packet
- required score-vs-offset improvement:
  - offset curve must be cleaner and more structured than `V0`
- required positive-minus-negative offset-gap improvement:
  - the offset gap must exceed `V0`
- required evidence that the result is not a uniform score shift:
  - overall score-level shift alone cannot explain the observed gain
- seed consistency rule:
  - the mechanism signal must appear in at least two of the three seeds

## 9. Predeclared failure criteria
Implementation must stop if any of these occur:
- mean accuracy loses to `V0`
- mean F1 loses to `V0`
- score-vs-offset structure is not cleaner than `V0`
- positive-minus-negative offset gap does not improve
- the effect can still be explained by score-surface elevation
- any gain appears in only one seed

## 10. Minimal implementation boundary
- exact files expected to change:
  - `src/qrope/qsim.py`
  - `src/qrope/run.py`
  - `tests/` files required for the new path
- exact files not allowed to change:
  - remote/cloud adapter paths
  - benchmark/dataset expansion paths outside the fixed synthetic packet
- tests required before first run:
  - deterministic comparator behavior
  - observable path coverage
  - packet-runner integration
- diagnostics required per run:
  - score-vs-offset
  - offset-gap
  - overall score-level shift
  - per-seed summary

## 11. Budget and scope guardrails
- Quandela credits allowed: `0`
- IBM remote allowed: `no`
- broad benchmark expansion allowed: `no`
- new variant branching allowed: `only V_new_explicit_interference`

## 12. Decision request
- Why should Quantyra approve implementation of this restart proposal?
  - because it is the first future mechanism candidate in this repo that directly targets the known failure mode with a materially different comparator and a predeclared falsification packet
- What is the smallest decisive experiment?
  - implement only the interference comparator and parity-contrast observable on the fixed synthetic packet
- What result would make us stop immediately?
  - any mixed or score-shift-only result under the fixed packet

## Approval status
- current status: `draft only`
- implementation authorized: `no`

## Bottom line
This brief is strong enough to make a real restart decision.
It is not an approval by itself.
