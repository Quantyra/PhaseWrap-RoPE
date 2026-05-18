# Story template

## Story ID and title
S062 - Local observable screening implementation plan

## User value
As a research lead, I want the implementation plan for local observable screening, so we can test `q2` and `parity` without conflating that work with a new variant branch.

## Acceptance criteria
- The minimal code changes for local observable screening are specified
- The evaluation packet is locked
- The resulting question is explicitly framed as screening-path infrastructure, not algorithm novelty

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-alternative-observable-screening-plan-v1.md`
- `docs/research/q-rope-local-observable-bottleneck-analysis-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S061

## Risks
- The observable-screening implementation may show that the local screening path requires broader redesign than a readout swap alone.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 14:40 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:44 (Pacific/Honolulu)
- Decision: implement a configurable local readout layer for `weighted`, `q2`, and `parity`; keep the resulting work framed as local screening infrastructure rather than algorithm novelty.
