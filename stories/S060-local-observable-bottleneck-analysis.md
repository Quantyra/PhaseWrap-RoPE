# Story template

## Story ID and title
S060 - Local observable bottleneck analysis

## User value
As a research lead, I want the local readout observable analyzed against alternatives, so we can decide whether the current weighted-excitation observable is the main compression bottleneck before proposing any future mechanism-level variant.

## Acceptance criteria
- A zero-credit observable-analysis plan is defined for the local screening circuit
- Candidate observables to compare are specified
- A decision framework is recorded for whether a future branch should target observable design or deeper mechanism redesign

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-phase-to-score-coupling-path-analysis-v1.md`
- `docs/research/q-rope-v3-v4-token-to-score-sensitivity-v1.md`

## Out of scope
- Paid remote execution
- Immediate new variant implementation

## Dependencies
- S059

## Risks
- Observable analysis may show that the current local screening score is too compressive to support reliable local promotion decisions without another simulator-path redesign.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 14:28 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:35 (Pacific/Honolulu)
- Decision: weighted mean excitation is a real compression bottleneck, but richer observables alone still do not create strong class separation, so any future mechanism-level branch must consider observable design and stronger post-phase mixing together.
