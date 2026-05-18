# Story template

## Story ID and title
S220 - Continuous target implementation

## User value
As a research lead, I want the approved continuous target path implemented and run on its fixed first packet, so the repo can test whether the line survives stronger symbolic regression baselines.

## Acceptance criteria
- Implement only the approved task, candidate, and control stack
- Run the fixed first packet
- Emit auditable diagnostics for all variants

## Outputs
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Dependencies
- S219
