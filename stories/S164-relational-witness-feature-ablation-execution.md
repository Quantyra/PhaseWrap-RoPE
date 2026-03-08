# Story template

## Story ID and title
S164 - Relational witness feature-ablation execution

## User value
As a research lead, I want the witness branch tested under one bounded feature-group ablation packet, so we can determine whether the result depends on a narrow subset of the approved relational schema.

## Acceptance criteria
- Implement masking for the fixed witness feature groups only
- Execute the fixed three-seed ablation packet
- Summarize degradation against the full witness model
- Keep the branch on the same task and local backend only

## Outputs
- `src/qrope/`
- `tests/`
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-relational-witness-feature-ablation-plan-v1.md`
- `docs/research/q-rope-first-relational-witness-packet-v1.md`
- `docs/research/q-rope-relational-witness-split-rotation-hardening-v1.md`

## Out of scope
- New tasks
- New seeds
- Remote execution
- New head families
- Rotated shadow packet expansion unless separately approved

## Dependencies
- S163

## Risks
- If ablation code changes the witness feature schema instead of only masking approved groups, the packet stops being interpretable.

## Unit tests (development stories only)
- Add focused ablation-mask tests only.

## Cycle time
- Start: 2026-03-08 11:46 (Pacific/Honolulu)
