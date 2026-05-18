# Story template

## Story ID and title
S189 - Dual-sector pair-reindex hardening plan

## User value
As a research lead, I want the next robustness check to change the paired concrete examples inside each sector pair bucket, so we can test whether the active witness branch survives a meaningful sample-selection perturbation.

## Acceptance criteria
- Define one deterministic pair-reindex control
- Keep task meaning unchanged
- Preserve local-only six-run packet scope

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-dual-sector-post-rotation-decision-v1.md`

## Out of scope
- New tasks
- New variants
- Remote execution

## Dependencies
- S188

## Risks
- If pair reindexing changes label logic or balance, the result stops being interpretable.

## Unit tests (development stories only)
- No new unit tests required in this planning step.

## Cycle time
- Start: 2026-03-08 18:19 (Pacific/Honolulu)
- End: 2026-03-08 18:24 (Pacific/Honolulu)
