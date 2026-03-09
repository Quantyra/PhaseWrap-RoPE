# Story template

## Story ID and title
S190 - Dual-sector pair-reindex hardening execution

## User value
As a research lead, I want the dual-sector witness branch rerun under a deterministic pair-reindex control, so we can see whether the current win survives a genuinely different balanced pairing of concrete examples.

## Acceptance criteria
- Implement only the bounded pair-reindex control
- Rerun the fixed six-run packet
- Summarize degradation against prior packets

## Outputs
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/`
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-dual-sector-pair-reindex-hardening-plan-v1.md`
- `docs/research/q-rope-dual-sector-post-rotation-decision-v1.md`

## Out of scope
- New tasks
- New variants
- Remote execution

## Dependencies
- S189

## Risks
- If pair reindexing changes balance or label logic, the hardening result stops being interpretable.

## Unit tests (development stories only)
- Add focused pair-reindex tests only.

## Cycle time
- Start: 2026-03-08 18:25 (Pacific/Honolulu)
