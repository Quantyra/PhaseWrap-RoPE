# Story template

## Story ID and title
S158 - Relational witness implementation

## User value
As a research lead, I want the approved relational witness restart implemented within the strict plan, so the repo can test the strongest new hybrid angle without losing validity discipline.

## Acceptance criteria
- Implement `V_future_relational_witness`
- Use only the approved feature schema
- Emit coefficient and intercept audits
- Execute only the fixed first packet

## Outputs
- `src/qrope/`
- `tests/`
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-relational-witness-implementation-plan-v1.md`
- `docs/research/q-rope-relational-witness-restart-brief-v1.md`

## Out of scope
- Remote execution
- Benchmark expansion
- Multiple candidate branches

## Dependencies
- S157

## Risks
- If the implementation exceeds the plan boundary, the restart loses its value as a constrained falsification test.

## Unit tests (development stories only)
- Add focused feature-schema and audit tests only.

## Cycle time
- Start: 2026-03-08 10:50 (Pacific/Honolulu)
- End: 2026-03-08 11:02 (Pacific/Honolulu)
