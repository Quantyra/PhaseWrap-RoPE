# Story template

## Story ID and title
S167 - Relational witness schema-compression execution

## User value
As a research lead, I want the witness branch tested under one bounded schema-compression packet, so we can determine whether the current positive result survives on a cleaner relational feature core.

## Acceptance criteria
- Implement the fixed schema views only
- Execute the fixed three-seed packet
- Summarize degradation against `full`
- Keep the branch on the same task and local backend only

## Outputs
- `src/qrope/`
- `tests/`
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-relational-witness-schema-compression-plan-v1.md`
- `docs/research/q-rope-relational-witness-schema-compression-v1.md`
- `docs/research/q-rope-relational-witness-feature-ablation-v1.md`

## Out of scope
- New tasks
- New seeds
- Remote execution
- New head families
- Second-wave decomposition controls

## Dependencies
- S166

## Risks
- If the implementation drifts from the fixed schema views, the packet stops answering the intended mechanism question.

## Unit tests (development stories only)
- Add focused schema-mask tests only.

## Cycle time
- Start: 2026-03-08 12:39 (Pacific/Honolulu)
- End: 2026-03-08 12:55 (Pacific/Honolulu)
