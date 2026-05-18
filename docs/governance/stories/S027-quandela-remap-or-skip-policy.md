# Story template

## Story ID and title
S027 - Quandela remap or skip policy

## User value
As a research lead, I want an explicit policy for provider-rejected Quandela parameter points, so remote coverage gaps are handled consistently rather than ad hoc.

## Acceptance criteria
- One policy is chosen and documented: remap, skip, or fail-fast by design.
- The policy is reflected in code and in the supplemental evidence note.
- A short impact note states whether prior Quandela artifacts remain comparable.

## Outputs
- `src/qrope/qphotonic.py`
- `docs/research/`
- `docs/governance/stories/`

## Evidence and references
- `docs/research/q-rope-quandela-hardening-note-v1.md`
- `docs/research/q-rope-matched-remote-supplemental-note-v1.md`

## Out of scope
- Full historical rerun of all Quandela artifacts
- Manuscript drafting

## Dependencies
- S026

## Risks
- Any remap weakens direct comparability with earlier Quandela supplemental results.

## Unit tests (development stories only)
- Add focused coverage if code changes are made.

## Cycle time
- Start: 2026-03-06 07:30 (Pacific/Honolulu)
- End: 2026-03-06 07:43 (Pacific/Honolulu)
- Total: 00:13

## Notes
- Completed with an explicit sample-level skip policy in code.
- Policy is honest but insufficient: seed `123` / `V2` and `V3` still fail because too few samples survive after skips.
- Next step should move to provider-path fallback or a semantically explicit remap decision.
