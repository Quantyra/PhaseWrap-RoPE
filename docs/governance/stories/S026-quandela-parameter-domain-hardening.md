# Story template

## Story ID and title
S026 - Quandela parameter-domain hardening

## User value
As a research lead, I want the Quandela adapter hardened against provider-rejected parameter regions, so remote seed coverage is not silently constrained by undocumented platform behavior.

## Acceptance criteria
- The specific provider-rejected parameter regime is documented or bounded in code.
- A mitigation strategy is selected: clamp, remap, or explicit skip policy.
- Evidence note states whether the mitigation changes the interpretation of prior remote runs.

## Outputs
- `src/qrope/qphotonic.py`
- `docs/research/`
- `docs/governance/stories/`

## Evidence and references
- `docs/research/q-rope-matched-remote-supplemental-note-v1.md`

## Out of scope
- Full remote rerun of all prior artifacts
- Manuscript drafting

## Dependencies
- S025

## Risks
- Any remapping may break comparability with prior Quandela supplemental artifacts.

## Unit tests (development stories only)
- Add focused coverage if code changes are made.

## Cycle time
- Start: 2026-03-06 07:05 (Pacific/Honolulu)
- End: 2026-03-06 07:29 (Pacific/Honolulu)
- Total: 00:24

## Notes
- Completed with retry/cache-reset hardening and explicit bounded failure surfacing in `qrope.qphotonic`.
- Hardening recovered seed `123` / `V0` but not seed `123` / `V2` or `V3`.
- Next step should choose an explicit remap or skip policy for the remaining blocked parameter region.
