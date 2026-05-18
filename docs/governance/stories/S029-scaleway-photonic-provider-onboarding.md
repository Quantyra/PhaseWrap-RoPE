# Story template

## Story ID and title
S029 - Scaleway photonic provider onboarding

## User value
As a research lead, I want a fallback photonic provider path onboarded, so photonic remote execution is not blocked by direct-Quandela instability.

## Acceptance criteria
- Required Scaleway account/project/API-key steps are documented.
- Required environment variables are defined.
- A minimal Perceval `ScalewaySession` connectivity path is ready to test once credentials exist.

## Outputs
- `docs/process/`
- `docs/governance/stories/`
- `scripts/`

## Evidence and references
- `docs/research/q-rope-photonic-provider-fallback-decision-v1.md`

## Out of scope
- Full Scaleway backend integration unless credentials are already available
- Manuscript drafting

## Dependencies
- S028

## Risks
- Scaleway may change cost, session semantics, or availability relative to direct Quandela.

## Unit tests (development stories only)
- n/a unless code changes are required.

## Cycle time
- Start: 2026-03-06 08:06 (Pacific/Honolulu)
- End: 2026-03-06 08:15 (Pacific/Honolulu)
- Total: 00:09

## Notes
- Completed with checklist, env-var placeholders, and a minimal `ScalewaySession` connectivity script.
- This step did not require remote execution and did not consume Quandela credits.
