# Story template

## Story ID and title
S028 - Photonic provider fallback decision

## User value
As a research lead, I want a concrete fallback decision for photonic remote execution, so the project is not blocked on an unstable Quandela submission path.

## Acceptance criteria
- Decide whether to stay on direct Quandela only, add a fallback provider path, or freeze Quandela supplemental expansion.
- Document the decision and rationale.
- State impact on prior supplemental evidence and future remote execution scope.

## Outputs
- `docs/research/`
- `docs/governance/stories/`

## Evidence and references
- `docs/research/q-rope-quandela-hardening-note-v1.md`
- `docs/research/q-rope-quandela-remap-skip-note-v1.md`

## Out of scope
- Full implementation of a new provider path unless the decision is immediate and low-risk
- Manuscript drafting

## Dependencies
- S027

## Risks
- A fallback provider may change cost, latency, or circuit compatibility.

## Unit tests (development stories only)
- n/a unless code changes are made.

## Cycle time
- Start: 2026-03-06 07:44 (Pacific/Honolulu)
- End: 2026-03-06 08:05 (Pacific/Honolulu)
- Total: 00:21

## Notes
- Completed with decision: do not treat a paid direct-Quandela plan as the primary fix.
- Chosen fallback direction: Perceval via `ScalewaySession`.
- Direct Quandela remains usable for limited supplemental evidence, but not as the sole photonic path.
