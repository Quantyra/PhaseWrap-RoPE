# Story template

## Story ID and title
S170 - Relational witness symbolic-control execution

## User value
As a research lead, I want the compressed witness branch compared against one bounded symbolic control, so we can determine whether the current positive result still exceeds a fair direct non-quantum relational baseline.

## Acceptance criteria
- Implement only the fixed symbolic sector-one-hot control
- Execute the fixed three-seed packet
- Compare `V_future_relational_witness` (`contrasts_only`) against the symbolic control
- Keep the branch on the same task and local backend only

## Outputs
- `src/qrope/`
- `tests/`
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-relational-witness-symbolic-control-plan-v1.md`
- `docs/research/q-rope-relational-witness-symbolic-control-v1.md`
- `docs/research/q-rope-relational-witness-schema-compression-v1.md`

## Out of scope
- New tasks
- New seeds
- Remote execution
- Second symbolic control families

## Dependencies
- S169

## Risks
- If the symbolic control uses more than sector one-hot inputs, the control stops being fair and bounded.

## Unit tests (development stories only)
- Add focused symbolic-control tests only.

## Cycle time
- Start: 2026-03-08 13:13 (Pacific/Honolulu)
- End: 2026-03-08 13:27 (Pacific/Honolulu)
