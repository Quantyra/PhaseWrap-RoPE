# Story template

## Story ID and title
S061 - Alternative observable screening plan

## User value
As a research lead, I want a zero-credit plan for screening alternative local observables, so we can decide whether the local screening path itself is worth upgrading before any new mechanism-level variant is proposed.

## Acceptance criteria
- Candidate observables for screening are selected
- The local decision criteria are specified
- The plan states whether this is a screening-path redesign question or a new-variant question

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-local-observable-bottleneck-analysis-v1.md`
- `docs/research/q-rope-phase-to-score-coupling-path-analysis-v1.md`

## Out of scope
- Paid remote execution
- Immediate new variant implementation

## Dependencies
- S060

## Risks
- Alternative observable screening may show that the local screening path itself needs redesign before it can support reliable future variant decisions.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 14:35 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:40 (Pacific/Honolulu)
- Decision: the next step is a local screening-path redesign question focused on `q2` and `parity`, not a new-variant question.
