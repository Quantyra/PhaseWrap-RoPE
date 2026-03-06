# Story template

## Story ID and title
S040 - V4b clipped ratio-controlled design

## User value
As a research lead, I want a more targeted `V4` redesign, so we can test a credible stability-oriented successor instead of spending time on a weak damped-only variant.

## Acceptance criteria
- A concrete `V4b` design is specified
- The design directly addresses the damped-only `V4` failure mode
- A zero-credit local validation plan is defined

## Outputs
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-v4-redesign-and-gate-tightening-v1.md`

## Out of scope
- Paid remote execution
- Broad benchmark reruns

## Dependencies
- S039

## Risks
- `V4b` may still be too weak or too brittle if the clipping/ratio controls are not calibrated carefully.

## Unit tests (development stories only)
- None unless code implementation starts in this story.

## Cycle time
- Start: 2026-03-06 10:42 (Pacific/Honolulu)
- End: 2026-03-06 11:01 (Pacific/Honolulu)

## Notes
- Keep this zero-credit until a concrete implementation is ready.
- Completed with a concrete shared-layer design, backend translation policy, and zero-credit local validation gate for `V4b`.
