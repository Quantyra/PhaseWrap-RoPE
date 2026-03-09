# Story template

## Story ID and title
S184 - Dual-sector token-renaming hardening execution

## User value
As a research lead, I want the dual-sector witness branch rerun under a deterministic global token-renaming control, so we can see whether the current win survives lexical symbol renaming.

## Acceptance criteria
- Implement only the bounded token-renaming control
- Rerun the fixed six-run packet
- Summarize degradation against the original and slot-swap packets

## Outputs
- `src/qrope/synthetic.py`
- `tests/`
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-dual-sector-token-renaming-hardening-plan-v1.md`
- `docs/research/q-rope-dual-sector-slot-swap-hardening-v1.md`

## Out of scope
- New tasks
- New variants
- Remote execution

## Dependencies
- S183

## Risks
- If the token-renaming control changes anything beyond symbol identity, the hardening result stops being interpretable.

## Unit tests (development stories only)
- Add focused token-renaming tests only.

## Cycle time
- Start: 2026-03-08 17:35 (Pacific/Honolulu)
