# Story template

## Story ID and title
S193 - Dual-sector symbolic-interaction control execution

## User value
As a research lead, I want the active witness branch compared against one stronger symbolic relational control with explicit sector-pair interaction terms, so we can see whether the current win survives a fairer bounded baseline.

## Acceptance criteria
- Implement one bounded symbolic interaction control only
- Rerun the fixed six-run packet
- Summarize the result against the witness branch

## Outputs
- `src/qrope/run.py`
- `tests/`
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-dual-sector-post-pair-reindex-decision-v1.md`
- `docs/research/q-rope-dual-sector-pair-reindex-hardening-v1.md`

## Out of scope
- New tasks
- New variants beyond the single stronger control
- Remote execution

## Dependencies
- S192

## Risks
- If the stronger control is made too flexible, the test stops being fair and becomes trivial.

## Unit tests (development stories only)
- Add focused symbolic-interaction control tests only.

## Cycle time
- Start: 2026-03-08 18:48 (Pacific/Honolulu)
- End: 2026-03-08 18:57 (Pacific/Honolulu)
