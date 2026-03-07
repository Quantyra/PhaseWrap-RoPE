# Story template

## Story ID and title
S069 - Post-RZ mixing implementation plan

## User value
As a research lead, I want the minimal implementation plan for post-`RZ` mixing screening, so we can test stronger phase-to-amplitude conversion without conflating it with a new variant branch.

## Acceptance criteria
- The minimal code changes for configurable local mixing presets are specified
- The evaluation packet is locked
- The work remains framed as local mechanism screening on `V3`

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-post-rz-mixing-screening-plan-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S068

## Risks
- The implementation may show that modest mixing changes are too weak, implying a larger local circuit redesign is needed later.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 15:15 (Pacific/Honolulu)
