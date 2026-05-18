# Story template

## Story ID and title
S056 - Post-calibration variant reassessment

## User value
As a research lead, I want the active variant decision reassessed after robust calibration, so we can decide whether `V4` still deserves primary attention or should return to exploratory status.

## Acceptance criteria
- The post-calibration evidence is compared against the pre-calibration local packet
- A decision is recorded on active local reference status (`V3` vs `V4`)
- The next zero-credit local track is defined

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-v4-robust-calibration-local-implementation-v1.md`
- `docs/research/q-rope-v4-vs-v3-larger-local-packet-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S055

## Risks
- Variant reassessment may collapse the current `V4` branch back to exploratory status, reducing the immediate positive narrative.

## Unit tests (development stories only)
- No new unit tests required unless new code changes are introduced.

## Cycle time
- Start: 2026-03-06 14:04 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:10 (Pacific/Honolulu)
- Decision: return `V3` to primary local reference status and demote `V4` to exploratory status pending score-geometry diagnostics.
