# Story template

## Story ID and title
S331 - Transition orbit pair-reindex hardening

## User value
As a research lead, I want to know whether the orbit branch survives a concrete pairing perturbation, so positive first-packet results are not over-interpreted.

## Acceptance criteria
- rerun the fixed packet with `pair_reindex = 1`
- summarize mean MAE and rank correlation
- decide the next bounded step

## Outputs
- `docs/research/`
- `logs/ablation_runs/summary/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Dependencies
- S330
