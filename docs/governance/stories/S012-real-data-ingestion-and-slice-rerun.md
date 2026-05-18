# Story template

## Story ID and title
S012 - Real data ingestion and slice rerun

## User value
As a research lead, I want real dataset ingestion wired for at least one benchmark slice, so ablation metrics move from synthetic fallback to domain-relevant evidence.

## Acceptance criteria
- Local dataset file exists for at least one target dataset (`yelp` or `imdb`).
- Real-mode run executes without synthetic fallback for one variant.
- Summary/report clearly separate synthetic and real-data runs.

## Outputs
- `data/<dataset>.jsonl` (or documented loader path)
- Updated `logs/ablation_runs/summary/summary_v1.csv`
- Updated `logs/ablation_runs/summary/report_v1.md`

## Evidence and references
- `stories/S011-train-inference-integration-for-real-metrics.md`
- `docs/research/q-rope-ablation-runbook-v1.md`

## Out of scope
- Full production-scale dataset pipeline.

## Dependencies
- S011

## Risks
- Data availability/licensing constraints can delay real-data ingestion.

## Unit tests (development stories only)
- Add test for local dataset loader path when file exists.

## Cycle time
- Start: 2026-03-05 08:40 (Pacific/Honolulu)
- End: 2026-03-05 08:52 (Pacific/Honolulu)
- Total: 00:12

## Notes
- This is the minimum bridge from synthetic validation to domain-relevant evidence.
- Completion: local dataset file `data/yelp.jsonl` added and real-mode run produced `data_mode=local_jsonl` artifact (`v3-yelp-local-s123`).
- Summary/report updated; local dataset loader path test added and passing.
