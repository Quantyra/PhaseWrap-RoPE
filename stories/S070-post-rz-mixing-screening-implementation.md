# Story template

## Story ID and title
S070 - Post-RZ mixing screening implementation

## User value
As a research lead, I want the local post-`RZ` mixing presets implemented and screened, so we can directly test whether stronger phase-to-amplitude conversion improves the primary `V3` path.

## Acceptance criteria
- Configurable local mixing presets are implemented
- Focused tests are updated
- The zero-credit `V3` parity packet runs for `mix_v0`, `mix_v1`, and `mix_v2`

## Outputs
- `src/qrope/`
- `tests/`
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-post-rz-mixing-implementation-plan-v1.md`

## Out of scope
- Paid remote execution
- New variant design

## Dependencies
- S069

## Risks
- The screen may show that modest mixing changes are insufficient, pushing the project toward a larger local circuit redesign question.

## Unit tests (development stories only)
- Add or update focused coverage as needed.

## Cycle time
- Start: 2026-03-06 15:19 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:11 (Pacific/Honolulu)
- Decision: `HOLD`. `mix_v2` was the only preset strong enough to trigger a weighted shadow check, but the parity-only gain did not survive strongly enough across `yelp` and `amazon` to justify branch promotion or remote spend.
