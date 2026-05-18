# Story template

## Story ID and title
S133 - Pair-state sector-permutation control implementation

## User value
As a research lead, I want the smallest sector-permutation control implemented and executed, so we can determine whether the pair-state win is genuinely relational or too directly aligned to the synthetic label rule.

## Acceptance criteria
- Implement exactly one `sector_permuted` control mode
- Reuse the existing pair-state skeleton
- Run the fixed synthetic packet on seeds `42`, `123`, `777`
- Compare aligned vs permuted outcomes

## Outputs
- `src/qrope/`
- `tests/`
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-pairstate-validity-audit-v1.md`
- `docs/research/q-rope-pairstate-sector-alignment-control-v1.md`
- `docs/research/q-rope-first-pairstate-synthetic-packet-v1.md`

## Out of scope
- New datasets
- Remote execution
- Multiple control families

## Dependencies
- S132

## Risks
- If the control is implemented too broadly, the branch will lose its causal interpretability.

## Unit tests (development stories only)
- Add focused tests for control-mode aggregation only.

## Cycle time
- Start: 2026-03-07 20:18 (Pacific/Honolulu)
- End: 2026-03-07 20:32 (Pacific/Honolulu)
