# Story template

## Story ID and title
S181 - Dual-sector slot-swap hardening execution

## User value
As a research lead, I want the dual witness branch rerun under a deterministic slot-swap control, so we can see whether the current win survives observation-slot exchange.

## Acceptance criteria
- Implement only the bounded slot-swap control
- Rerun the fixed six-run packet
- Summarize degradation against the original packet

## Outputs
- `src/qrope/synthetic.py`
- `tests/`
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-dual-sector-slot-swap-hardening-plan-v1.md`
- `docs/research/q-rope-dual-sector-agreement-first-packet-v1.md`

## Out of scope
- New tasks
- New variants
- Remote execution

## Dependencies
- S180

## Risks
- If the slot-swap control changes anything other than observation order, the hardening result stops being interpretable.

## Unit tests (development stories only)
- Add focused slot-swap tests only.

## Cycle time
- Start: 2026-03-08 14:55 (Pacific/Honolulu)
- End: 2026-03-08 17:20 (Pacific/Honolulu)
