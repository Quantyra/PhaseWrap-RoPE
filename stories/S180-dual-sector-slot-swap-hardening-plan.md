# Story template

## Story ID and title
S180 - Dual-sector slot-swap hardening plan

## User value
As a research lead, I want the next hardening step defined around slot-swap symmetry, so we can test whether the dual witness branch is using agreement structure rather than slot identity.

## Acceptance criteria
- Define one bounded slot-swap control
- Keep the same task and seeds
- Avoid broadening scope

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-dual-sector-agreement-post-packet-decision-v1.md`
- `docs/research/q-rope-dual-sector-agreement-first-packet-v1.md`

## Out of scope
- Implementation
- Remote execution
- New tasks

## Dependencies
- S179

## Risks
- If symmetry is not checked now, a strong first packet could still be over-interpreted.

## Unit tests (development stories only)
- No new unit tests required in this memo step.

## Cycle time
- Start: 2026-03-08 14:48 (Pacific/Honolulu)
