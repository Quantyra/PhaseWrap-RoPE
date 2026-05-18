# Story template

## Story ID and title
S334 - Transition orbit split-rotation hardening

## User value
As a research lead, I want to know whether the orbit branch survives split-rotation perturbation, so example-selection sensitivity is explicit.

## Acceptance criteria
- rerun the fixed packet with `split_rotation = 1`
- summarize mean MAE and rank correlation
- decide whether the control was meaningful

## Outputs
- `docs/research/`
- `logs/ablation_runs/summary/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Dependencies
- S333
