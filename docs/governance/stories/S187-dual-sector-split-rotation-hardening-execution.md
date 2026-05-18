# Story template

## Story ID and title
S187 - Dual-sector split-rotation hardening execution

## User value
As a research lead, I want the dual-sector witness branch rerun under a deterministic split-rotation control, so we can see whether the current win survives a different balanced within-bucket sample selection.

## Acceptance criteria
- Implement no new mechanism work
- Rerun the fixed six-run packet with `split_rotation = 1`
- Summarize degradation against the original, slot-swap, and token-renaming packets

## Outputs
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-dual-sector-token-renaming-post-hardening-decision-v1.md`
- `docs/research/q-rope-dual-sector-agreement-first-packet-v1.md`

## Out of scope
- New tasks
- New variants
- Remote execution

## Dependencies
- S186

## Risks
- If split rotation changes anything beyond example selection, the hardening result stops being interpretable.

## Unit tests (development stories only)
- Reuse the existing split-rotation path; no new unit tests required unless runner behavior changes.

## Cycle time
- Start: 2026-03-08 18:02 (Pacific/Honolulu)
- End: 2026-03-08 18:14 (Pacific/Honolulu)
