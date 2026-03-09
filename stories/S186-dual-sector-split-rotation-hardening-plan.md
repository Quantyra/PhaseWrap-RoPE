# Story template

## Story ID and title
S186 - Dual-sector split-rotation hardening plan

## User value
As a research lead, I want the next validity check to probe robustness to deterministic sample selection, so we can see whether the active witness branch depends on one favorable within-bucket draw.

## Acceptance criteria
- Define one deterministic split-rotation control
- Keep task meaning unchanged
- Preserve local-only six-run packet scope

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-dual-sector-token-renaming-post-hardening-decision-v1.md`

## Out of scope
- New tasks
- New variants
- Remote execution

## Dependencies
- S185

## Risks
- If split rotation changes task balance or the fixed packet scope, the result stops being comparable.

## Unit tests (development stories only)
- No new unit tests required in this planning step.

## Cycle time
- Start: 2026-03-08 17:56 (Pacific/Honolulu)
