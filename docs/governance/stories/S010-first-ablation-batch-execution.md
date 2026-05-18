# Story template

## Story ID and title
S010 - First ablation batch execution

## User value
As a research lead, I want the first full `V0-V3` ablation batch executed, so we can move from planning to empirical evidence.

## Acceptance criteria
- All four variants run on Yelp/IMDb/Amazon with fixed seeds.
- Metrics are aggregated into `summary_v1.csv`.
- Initial comparison report is generated and reviewed for data quality.

## Outputs
- `logs/ablation_runs/`
- `logs/ablation_runs/summary/summary_v1.csv`
- `logs/ablation_runs/summary/report_v1.md`

## Evidence and references
- `docs/research/q-rope-ablation-runbook-v1.md`
- `configs/ablation/`

## Out of scope
- Final statistical interpretation for publication.

## Dependencies
- S009

## Risks
- Placeholder metrics pipeline may be mistaken for real experiment output if not labeled clearly.

## Unit tests (development stories only)
- Validate one run artifact schema against required fields.

## Cycle time
- Start: 2026-03-05 08:24 (Pacific/Honolulu)
- End: 2026-03-05 08:31 (Pacific/Honolulu)
- Total: 00:07

## Notes
- Mark all bootstrap outputs as dry-run until model training is wired.
- Completion: full matrix executed (`4 variants x 3 datasets x 3 seeds = 36 runs`) and summary artifacts regenerated.
- Status constraint: all metrics are dry-run placeholders (`dry_run=True`, zero-valued model metrics) pending training/inference integration.
