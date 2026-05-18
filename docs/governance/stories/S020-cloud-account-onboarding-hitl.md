# Story template

## Story ID and title
S020 - Cloud account onboarding (HITL)

## User value
As a research lead, I want cloud account onboarding tracked with explicit human-in-the-loop steps, so photonic and IBM cloud execution can proceed safely.

## Acceptance criteria
- Checklist exists with provider-specific account/token steps.
- Required environment variables are documented.
- Story clearly marks waiting-on-user actions.

## Outputs
- `docs/process/cloud-account-onboarding-checklist.md`

## Evidence and references
- `docs/research/q-rope-open-source-and-cloud-strategy-v1.md`

## Out of scope
- Executing cloud jobs without valid credentials.

## Dependencies
- S019

## Risks
- Delays due to account provisioning and token access.

## Unit tests (development stories only)
- n/a

## Cycle time
- Start: 2026-03-05 10:30 (Pacific/Honolulu)
- End: 2026-03-05 10:34 (Pacific/Honolulu)
- Total: 00:04

## Notes
- Completion: checklist authored. Status now `WAITING_USER` for account/token provisioning.
- Update: IBM and Quandela onboarding are complete with successful local connectivity checks.
- Update: Xanadu Cloud is deferred as non-operational/unavailable for the current project path.
- Current HITL scope is satisfied for active providers (`IBM`, `Quandela`).
