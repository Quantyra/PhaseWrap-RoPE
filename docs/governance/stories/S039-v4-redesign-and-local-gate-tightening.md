# Story template

## Story ID and title
S039 - V4 redesign and local gate tightening

## User value
As a research lead, I want the `V4` screening gate tightened and the next redesign options defined, so we stop spending time on non-informative local comparisons and only promote credible variants.

## Acceptance criteria
- The local screening policy explicitly excludes non-variant-sensitive backends
- The failure mode of damped-only `V4` is documented
- A concrete redesign direction for the next `V4` iteration is specified

## Outputs
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-v4-local-comparison-packet-v1.md`

## Out of scope
- Paid remote execution
- Broad benchmark reruns

## Dependencies
- S038

## Risks
- The next redesign may still fail if the local gate remains too small or underinformative.

## Unit tests (development stories only)
- None unless gating logic in code changes.

## Cycle time
- Start: 2026-03-06 10:32 (Pacific/Honolulu)
- End: 2026-03-06 10:42 (Pacific/Honolulu)

## Notes
- This story should stay zero-credit unless a later redesign clearly passes the tightened local gate.
- Completed with an explicit gate change excluding `sim_local` from variant promotion decisions and a redesign direction for the next `V4` iteration.
