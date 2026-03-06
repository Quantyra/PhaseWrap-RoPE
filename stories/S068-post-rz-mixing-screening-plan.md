# Story template

## Story ID and title
S068 - Post-RZ mixing screening plan

## User value
As a research lead, I want a zero-credit plan for screening stronger post-`RZ` mixing on the primary local reference path, so we can determine whether the current bottleneck is solvable without opening a new variant branch prematurely.

## Acceptance criteria
- The post-`RZ` mixing question is scoped concretely
- The local evaluation packet is defined
- The work is explicitly framed as mechanism screening on the primary path, not a new algorithm branch

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-next-branch-question-selection-v1.md`
- `docs/research/q-rope-phase-to-score-coupling-path-analysis-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S067

## Risks
- Mechanism screening may show that the current local path needs a broader circuit redesign rather than a modest mixing change.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 15:11 (Pacific/Honolulu)
