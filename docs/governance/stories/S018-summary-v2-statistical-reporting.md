# Story template

## Story ID and title
S018 - Summary v2 statistical reporting

## User value
As a research lead, I want statistical reporting artifacts (CI/effect-size fields), so we can evaluate whether observed differences are publication-relevant.

## Acceptance criteria
- Generate `summary_v2.csv` with variance/CI placeholders or computed fields from current runs.
- Generate `report_v2.md` with per-variant comparisons (`V3` vs others).
- Document remaining gaps to full significance package.

## Outputs
- `logs/ablation_runs/summary/summary_v2.csv`
- `logs/ablation_runs/summary/report_v2.md`

## Evidence and references
- `docs/research/q-rope-phase2-rigor-and-hardware-plan-v1.md`
- `logs/ablation_runs/summary/summary_v1.csv`

## Out of scope
- Full cloud hardware execution.

## Dependencies
- S017

## Risks
- Limited seed count can produce unstable CI estimates.

## Unit tests (development stories only)
- Add/extend report generation test for v2 outputs.

## Cycle time
- Start: 2026-03-05 10:34 (Pacific/Honolulu)
- End: 2026-03-05 10:44 (Pacific/Honolulu)
- Total: 00:10

## Notes
- This story starts phase-2 quantitative rigor implementation.
- Completion: generated `summary_v2.csv` and `report_v2.md` with means, stddev, CI95, gate/depth means, and `V3` delta comparisons.
- Remaining gap: current CI/effect estimates are still limited by small handcrafted dataset sizes and low seed counts.
