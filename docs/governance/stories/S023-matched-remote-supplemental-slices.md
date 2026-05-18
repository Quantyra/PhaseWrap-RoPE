# Story template

## Story ID and title
S023 - Matched remote supplemental slices

## User value
As a research lead, I want matched supplemental remote slices across Quandela and IBM, so the two cloud backends can be compared on the same fixed evidence packet.

## Acceptance criteria
- Fixed matched slice definition exists for at least one dataset.
- Both remote backends are executed on the same slice and variant set.
- Reporting note summarizes comparator limitations and backend asymmetries.

## Outputs
- `docs/research/`
- `logs/ablation_runs/`
- `logs/ablation_runs/summary/`

## Evidence and references
- `docs/research/q-rope-quandela-remote-backend-v1.md`
- `docs/research/q-rope-ibm-runtime-backend-v1.md`

## Out of scope
- Full remote matrix across all seeds and datasets
- Manuscript drafting

## Dependencies
- S021
- S022

## Risks
- Cross-provider comparability may still be weak because circuit families differ.

## Unit tests (development stories only)
- Update local unit coverage only if helper logic changes.

## Cycle time
- Start: 2026-03-06 05:04 (Pacific/Honolulu)
- End: 2026-03-06 05:49 (Pacific/Honolulu)
- Total: 00:45

## Notes
- Completed with matched `yelp`, `seed=42`, 12-sample remote slices for `V0` and `V3` on both Quandela and IBM.
- Directional result matched across providers on this slice: `V3` outperformed `V0` in accuracy.
- Comparator limitations are documented in `docs/research/q-rope-matched-remote-supplemental-note-v1.md`.
