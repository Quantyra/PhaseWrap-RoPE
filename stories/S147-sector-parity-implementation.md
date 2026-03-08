# Story template

## Story ID and title
S147 - Sector-parity implementation

## User value
As a research lead, I want the approved sector-parity restart implemented within the strict plan, so the repo can test the strongest remaining restart path without reintroducing uncontrolled scope.

## Acceptance criteria
- Implement `synthetic_sector_parity_binary`
- Implement `V_future_sector_contrast_pairstate`
- Add only focused tests and diagnostics
- Execute only the fixed first packet

## Outputs
- `src/qrope/`
- `tests/`
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-sector-parity-implementation-plan-v1.md`
- `docs/research/q-rope-sector-parity-restart-brief-v2.md`

## Out of scope
- Remote execution
- Benchmark expansion
- Multiple candidate branches

## Dependencies
- S146

## Risks
- If the implementation exceeds the plan boundary, the restart loses interpretability before the first packet is even run.

## Unit tests (development stories only)
- Add focused generator and diagnostic tests only.

## Cycle time
- Start: 2026-03-08 09:41 (Pacific/Honolulu)
